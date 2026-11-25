"""Prepara una microcuenca DEM para el punto 2.

No sustituye la comprobacion hidrologica en QGIS: selecciona un punto de
salida reproducible cerca de la estacion y deja todos los calculos trazables.
"""
from __future__ import annotations

import csv
from PIL import Image
import heapq
import json
from pathlib import Path

import numpy as np
from shapely.geometry import box, mapping, Point
from shapely.ops import unary_union


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "cuenca_preparada"
OUT.mkdir(exist_ok=True)

ST_LAT, ST_LON, ST_ELEV = 48.9219, 9.9129, 432.0
# Punto sobre el cauce OSM mas cercano (Rötenbach/tributario), usado para
# corregir el outlet cuando se activa la validacion de 2.4.
FORCED_OUTLET = None
DEM = DATA / "N48E009_entorno_microcuenca.tif"
DEM_META = DATA / "N48E009_entorno_microcuenca.json"
CELL = 1.0 / 3600.0


def read_dem(path: Path, metadata_path: Path) -> tuple[np.ndarray, dict]:
    for required in (path, metadata_path):
        if not required.is_file():
            raise FileNotFoundError(f"Entrada no incluida: {required.relative_to(ROOT)}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    array = np.asarray(Image.open(path), dtype=float)
    expected = (metadata["source_window"]["height"], metadata["source_window"]["width"])
    if array.shape != expected:
        raise ValueError(f"Dimensiones DEM inesperadas: {array.shape}; esperadas {expected}")
    return array, metadata


def priority_fill(z: np.ndarray) -> np.ndarray:
    """Priority-flood fill of edge-connected depressions."""
    nrow, ncol = z.shape
    out = z.copy()
    seen = np.zeros(z.shape, dtype=bool)
    heap: list[tuple[float, int, int]] = []
    for r in range(nrow):
        for c in (0, ncol - 1):
            if not seen[r, c]:
                seen[r, c] = True
                heapq.heappush(heap, (out[r, c], r, c))
    for c in range(ncol):
        for r in (0, nrow - 1):
            if not seen[r, c]:
                seen[r, c] = True
                heapq.heappush(heap, (out[r, c], r, c))
    while heap:
        elev, r, c = heapq.heappop(heap)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if not (dr or dc):
                    continue
                rr, cc = r + dr, c + dc
                if rr < 0 or rr >= nrow or cc < 0 or cc >= ncol or seen[rr, cc]:
                    continue
                seen[rr, cc] = True
                if out[rr, cc] < elev:
                    out[rr, cc] = elev
                heapq.heappush(heap, (out[rr, cc], rr, cc))
    return out


def main() -> None:
    z, dem_meta = read_dem(DEM, DEM_META)
    nrow, ncol = z.shape
    filled = priority_fill(z)

    # Coordenadas preservadas de la ventana original, sin remuestreo.
    lat = float(dem_meta["lat_first_center"]) - np.arange(nrow) * CELL
    lon = float(dem_meta["lon_first_center"]) + np.arange(ncol) * CELL
    dx = 111320.0 * np.cos(np.deg2rad(lat)) / 3600.0
    dy = 111320.0 / 3600.0
    cell_area = np.broadcast_to((dx[:, None] * dy), z.shape).copy()

    # Direccion D8 hacia el vecino de mayor descenso en la superficie rellenada.
    to_r = np.full(z.shape, -1, dtype=np.int32)
    to_c = np.full(z.shape, -1, dtype=np.int32)
    for r in range(1, nrow - 1):
        for c in range(1, ncol - 1):
            best = 0.0
            dest = None
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if not (dr or dc):
                        continue
                    rr, cc = r + dr, c + dc
                    drop = filled[r, c] - filled[rr, cc]
                    if drop > best:
                        best, dest = drop, (rr, cc)
            if dest is not None:
                to_r[r, c], to_c[r, c] = dest

    # Acumulacion: procesar de mayor a menor elevacion.
    acc = cell_area.copy()
    order = np.argsort(filled.ravel())[::-1]
    for flat in order:
        r, c = divmod(int(flat), ncol)
        rr, cc = to_r[r, c], to_c[r, c]
        if rr >= 0:
            acc[rr, cc] += acc[r, c]

    sr = int(np.argmin(np.abs(lat - ST_LAT)))
    sc = int(np.argmin(np.abs(lon - ST_LON)))
    station = Point(float(lon[sc]), float(lat[sr]))
    # La estacion puede caer en una celda plana del DEM. Se usa como ancla la
    # celda de drenaje con acumulacion >=0.02 km2 mas cercana (snap hidrologico).
    dlat_grid = (lat[:, None] - ST_LAT) * 111320.0
    dlon_grid = (lon[None, :] - ST_LON) * 111320.0 * np.cos(np.deg2rad(ST_LAT))
    dist_grid = np.hypot(dlat_grid, dlon_grid)
    snap_mask = (acc >= 2e4) & (dist_grid <= 1500) & (to_r >= 0)
    if np.any(snap_mask):
        snap_flat = np.argmin(np.where(snap_mask, dist_grid, np.inf))
        ar, ac = divmod(int(snap_flat), ncol)
    else:
        ar, ac = sr, sc
    # Elegir salida cercana, con area 0.1-5 km2 y captacion que incluya el ancla.
    candidates = []
    for r in range(1, nrow - 1):
        for c in range(1, ncol - 1):
            area = acc[r, c]
            if not (1e5 <= area <= 5e6):
                continue
            dlat = (lat[r] - ST_LAT) * 111320.0
            dlon = (lon[c] - ST_LON) * 111320.0 * np.cos(np.deg2rad(ST_LAT))
            dist = float(np.hypot(dlat, dlon))
            if dist > 4500:
                continue
            # Revisar si la celda de la estacion drena hacia el candidato.
            rr, cc = ar, ac
            found = False
            for _ in range(nrow + ncol):
                if rr < 0 or cc < 0 or to_r[rr, cc] < 0:
                    break
                if rr == r and cc == c:
                    found = True
                    break
                nr, nc = to_r[rr, cc], to_c[rr, cc]
                if nr == rr and nc == cc:
                    break
                rr, cc = int(nr), int(nc)
            candidates.append((0 if found else 1, dist, -area, r, c, found))
    if not candidates:
        raise RuntimeError("No se encontro una salida con area entre 0.1 y 5 km2")
    # Seleccion automatica autorizada: probar centros de cauces OSM y elegir el
    # mas cercano a la estacion que conserve 0.1-5 km2 en el DEM.
    osm_candidates = []
    osm_path = DATA / "control_2_1" / "osm_outlet_context.json"
    if osm_path.exists():
        try:
            osm = json.loads(osm_path.read_text(encoding="utf-8"))
            for e in osm.get("elements", []):
                t = e.get("tags", {}); cc = e.get("center", {})
                if t.get("waterway") and cc.get("lat") and cc.get("lon"):
                    osm_candidates.append((float(cc["lat"]), float(cc["lon"]), t.get("name", ""), t.get("waterway", "")))
        except Exception:
            osm_candidates = []
    osm_valid = []
    for clat, clon, cname, ctype in osm_candidates:
        rr0 = int(np.argmin(np.abs(lat-clat))); cc0 = int(np.argmin(np.abs(lon-clon)))
        area0 = float(acc[rr0, cc0])
        if 1e5 <= area0 <= 5e6:
            ddlat=(lat[rr0]-ST_LAT)*111320; ddlon=(lon[cc0]-ST_LON)*111320*np.cos(np.deg2rad(ST_LAT))
            osm_valid.append((float(np.hypot(ddlat,ddlon)),rr0,cc0,area0,cname,ctype))
    if FORCED_OUTLET is not None:
        flat = np.argmin((lat[:, None]-FORCED_OUTLET[0])**2 + (lon[None, :]-FORCED_OUTLET[1])**2)
        orow, ocol = divmod(int(flat), ncol)
        basin_area = float(acc[orow, ocol])
        dlat = (lat[orow]-ST_LAT)*111320; dlon=(lon[ocol]-ST_LON)*111320*np.cos(np.deg2rad(ST_LAT))
        dist=float(np.hypot(dlat,dlon)); station_drains=False
        if not (1e5 <= basin_area <= 5e6):
            raise RuntimeError(f"El outlet forzado produce area fuera de 0.1-5 km2: {basin_area/1e6:.3f}")
    elif osm_valid:
        dist, orow, ocol, basin_area, osm_name, osm_type = sorted(osm_valid)[0]
        station_drains=False
    else:
        candidates.sort()
        _, dist, negarea, orow, ocol, station_drains = candidates[0]
        basin_area = -negarea

    # Mascara aguas arriba mediante recorrido inverso de las celdas.
    upstream = np.zeros(z.shape, dtype=bool)
    upstream[orow, ocol] = True
    stack = [(orow, ocol)]
    while stack:
        r, c = stack.pop()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < nrow and 0 <= cc < ncol and not upstream[rr, cc]:
                    if to_r[rr, cc] == r and to_c[rr, cc] == c:
                        upstream[rr, cc] = True
                        stack.append((rr, cc))

    # Geometria de la microcuenca como union de celdas DEM.
    cells = [box(float(lon[c] - CELL / 2), float(lat[r] - CELL / 2),
                 float(lon[c] + CELL / 2), float(lat[r] + CELL / 2))
             for r, c in zip(*np.where(upstream))]
    polygon = unary_union(cells).simplify(CELL / 5, preserve_topology=True)
    out_lat, out_lon = float(lat[orow]), float(lon[ocol])
    vals = z[upstream]
    grad_y, grad_x = np.gradient(filled, dy, dx.mean())
    slope = np.hypot(grad_x, grad_y)[upstream]
    # Trayectoria aproximada del cauce principal: desde la celda aguas arriba
    # con mayor acumulacion hasta el outlet.
    dist_up = np.where(upstream, np.hypot((np.indices(z.shape)[0]-orow)*dy, (np.indices(z.shape)[1]-ocol)*dx.mean()), -1)
    up_idx = np.where(dist_up == np.max(dist_up))
    cr, cc = int(up_idx[0][0]), int(up_idx[1][0])
    path = [(cr, cc)]; length_m = 0.0
    while not (cr == orow and cc == ocol):
        nr, nc = int(to_r[cr, cc]), int(to_c[cr, cc])
        if nr < 0 or nc < 0 or len(path) > nrow*ncol: break
        length_m += float(np.hypot((nr-cr)*dy, (nc-cc)*dx[cr]))
        cr, cc = nr, nc; path.append((cr, cc))
    channel_slope = float((z[path[0]] - z[path[-1]]) / length_m) if length_m > 0 else float('nan')
    path_coords = [[float(lon[c]), float(lat[r])] for r, c in path]

    # Salidas GIS y tablas reproducibles.
    with (OUT / "microcuenca_abtsgmuend.geojson").open("w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": [{
            "type": "Feature", "properties": {"station_id": "00020", "area_km2": basin_area / 1e6,
            "outlet_lat": out_lat, "outlet_lon": out_lon}, "geometry": mapping(polygon)}]}, f, ensure_ascii=False)
    with (OUT / "puntos_control.geojson").open("w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {"tipo": "estacion", "id": "00020"}, "geometry": mapping(station)},
            {"type": "Feature", "properties": {"tipo": "salida", "area_km2": basin_area / 1e6}, "geometry": mapping(Point(out_lon, out_lat))}
        ]}, f, ensure_ascii=False)
    with (OUT / "cauce_principal.geojson").open("w", encoding="utf-8") as f:
        json.dump({"type":"FeatureCollection","features":[{"type":"Feature","properties":{"length_m":length_m,"slope_m_m":channel_slope},"geometry":{"type":"LineString","coordinates":path_coords}}]}, f, ensure_ascii=False)
    with (OUT / "cuenca_resumen.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["campo", "valor"])
        rows = {"station_id": "00020", "station_lat": ST_LAT, "station_lon": ST_LON, "station_elev_m": ST_ELEV,
                "outlet_lat": out_lat, "outlet_lon": out_lon, "outlet_distance_m": round(dist, 1),
                "station_snap_lat": float(lat[ar]), "station_snap_lon": float(lon[ac]),
                "station_snap_distance_m": round(float(dist_grid[ar, ac]), 1),
                "area_km2": round(basin_area / 1e6, 5), "elev_min_m": round(float(vals.min()), 2),
                "elev_max_m": round(float(vals.max()), 2), "elev_mean_m": round(float(vals.mean()), 2),
                "slope_mean_pct": round(float(np.mean(slope) * 100), 3),
                "main_channel_length_m": round(length_m, 2), "main_channel_slope_m_m": round(channel_slope, 5),
                "station_inside_drainage": station_drains, "dem_source": "SRTM N48E009_entorno_microcuenca.tif (recorte sin remuestreo)"}
        w.writerows(rows.items())
    np.save(OUT / "microcuenca_mask.npy", upstream)
    np.save(OUT / "dem_ventana_m.npy", z.astype(np.float32))
    (OUT / "README.md").write_text(
        "# Microcuenca preparada\n\n"
        "La geometria se obtuvo con flujo D8 y priority-flood sobre SRTM N48E009. "
        "El punto de salida se selecciono cerca de la estacion DWD 00020, con area "
        "entre 0.1 y 5 km2. Verificar visualmente en QGIS antes de entregar.\n\n"
        "Archivos: `microcuenca_abtsgmuend.geojson`, `puntos_control.geojson`, "
        "`cuenca_resumen.csv`, `microcuenca_mask.npy` y `dem_ventana_m.npy`.\n", encoding="utf-8")
    print(json.dumps({"outlet_lat": out_lat, "outlet_lon": out_lon, "area_km2": basin_area / 1e6,
                      "distance_m": dist, "station_inside_drainage": station_drains}, ensure_ascii=False))


if __name__ == "__main__":
    main()
