"""Mapa estático de comprobación visual del outlet y la microcuenca.

Combina el MDE SRTM, el polígono derivado, los puntos de control y las
geometrías de cauces descargadas desde OpenStreetMap. No reemplaza una
inspección de campo ni la validación hidrológica del punto de salida.
"""
from pathlib import Path
from PIL import Image
import json
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BASE = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
DEM = BASE / "N48E009_entorno_microcuenca.tif"
DEM_META = BASE / "N48E009_entorno_microcuenca.json"
CUENCA = BASE / "cuenca_preparada" / "microcuenca_abtsgmuend.geojson"
PUNTOS = BASE / "cuenca_preparada" / "puntos_control.geojson"
CAUCE = BASE / "cuenca_preparada" / "cauce_principal.geojson"
OSM = BASE / "control_2_1" / "osm_water_geom.json"
OUT = BASE / "control_2_1" / "mapa_revision_visual.png"
OUT_ZOOM = BASE / "control_2_1" / "mapa_revision_visual_detalle.png"
CSV_OUT = BASE / "control_2_1" / "mapa_revision_distancias.csv"


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def main():
    for required in (DEM, DEM_META):
        if not required.is_file():
            raise FileNotFoundError(f"Entrada no incluida: {required.relative_to(ROOT)}")
    dem_meta = json.loads(DEM_META.read_text(encoding="utf-8-sig"))
    dem = np.asarray(Image.open(DEM), dtype=float)

    cuenca = json.loads(CUENCA.read_text(encoding="utf-8"))
    ring = np.asarray(cuenca["features"][0]["geometry"]["coordinates"][0])
    puntos = json.loads(PUNTOS.read_text(encoding="utf-8"))["features"]
    cauce = json.loads(CAUCE.read_text(encoding="utf-8"))["features"]
    outlet = next(f for f in puntos if f["properties"]["tipo"] == "salida")["geometry"]["coordinates"]
    station = next(f for f in puntos if f["properties"]["tipo"] == "estacion")["geometry"]["coordinates"]
    osm = json.loads(OSM.read_text(encoding="utf-8"))

    # Extensión con margen suficiente para ver el contexto de los cauces.
    xmin, xmax = 9.875, 9.955
    ymin, ymax = 48.895, 48.945
    lons = float(dem_meta["lon_first_center"]) + np.arange(dem.shape[1]) / 3600.0
    lats = float(dem_meta["lat_first_center"]) - np.arange(dem.shape[0]) / 3600.0
    # index rows for descending latitude
    rows = np.where((lats >= ymin) & (lats <= ymax))[0]
    cols = np.where((lons >= xmin) & (lons <= xmax))[0]
    sub = dem[rows.min():rows.max()+1, cols.min():cols.max()+1]
    ext = [lons[cols.min()], lons[cols.max()], lats[rows.max()], lats[rows.min()]]

    fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)
    im = ax.imshow(sub, extent=ext, cmap="terrain", alpha=0.82, origin="upper")
    levels = np.arange(np.nanmin(sub) // 25 * 25, np.nanmax(sub) + 25, 25)
    cs = ax.contour(lons[cols.min():cols.max()+1], lats[rows.min():rows.max()+1], sub,
                    levels=levels, colors="k", linewidths=0.25, alpha=0.35)
    ax.clabel(cs, levels[::2], inline=True, fontsize=6, fmt="%d m")

    ax.plot(ring[:, 0], ring[:, 1], color="#d62728", linewidth=2.2, label="Límite microcuenca")
    for f in cauce:
        g = f.get("geometry", {})
        if g.get("type") == "LineString":
            xy = np.asarray(g["coordinates"])
            ax.plot(xy[:, 0], xy[:, 1], color="black", linestyle="--", linewidth=1.5,
                    label="Cauce principal DEM", zorder=5)
    ax.scatter(*station, s=75, marker="^", color="#7b2cbf", edgecolor="white", zorder=6, label="Estación DWD 00020")
    ax.scatter(*outlet, s=80, marker="X", color="#111111", edgecolor="white", zorder=7, label="Outlet usado")

    # Dibujar geometrías OSM de cauces; se ignoran elementos sin geometría.
    named = []
    for el in osm.get("elements", []):
        geom = el.get("geometry") or []
        if len(geom) < 2:
            continue
        xs = [p["lon"] for p in geom]
        ys = [p["lat"] for p in geom]
        if max(xs) < xmin or min(xs) > xmax or max(ys) < ymin or min(ys) > ymax:
            continue
        tags = el.get("tags", {})
        waterway = tags.get("waterway", "")
        color = "#1976d2" if waterway in {"stream", "river", "canal", "drain", "ditch"} else "#4dabf7"
        ax.plot(xs, ys, color=color, linewidth=1.0, alpha=0.78, zorder=3,
                label="Cauce OSM" if not named else None)
        if tags.get("name"):
            # etiqueta sólo para los cauces que pasan cerca del outlet
            d = min(haversine_m(outlet[1], outlet[0], y, x) for x, y in zip(xs, ys))
            if d < 900:
                k = int(np.argmin([haversine_m(outlet[1], outlet[0], y, x) for x, y in zip(xs, ys)]))
                ax.text(xs[k], ys[k], tags["name"], fontsize=7, color="#075985", zorder=8)
                named.append((tags["name"], d))

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Longitud (°E)")
    ax.set_ylabel("Latitud (°N)")
    ax.set_title("Comprobación visual: microcuenca Abtsgmünd–Untergröningen\nMDE SRTM + cauces OSM + puntos de control")
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.02)
    cb.set_label("Elevación (m s.n.m.)")
    fig.savefig(OUT, dpi=220)
    plt.close(fig)

    # Segundo mapa ampliado para decidir si el outlet queda sobre el cauce.
    fig, ax = plt.subplots(figsize=(9, 7), constrained_layout=True)
    zx0, zx1, zy0, zy1 = 9.902, 9.922, 48.913, 48.924
    zcols = np.where((lons >= zx0) & (lons <= zx1))[0]
    zrows = np.where((lats >= zy0) & (lats <= zy1))[0]
    zsub = dem[zrows.min():zrows.max()+1, zcols.min():zcols.max()+1]
    zext = [lons[zcols.min()], lons[zcols.max()], lats[zrows.max()], lats[zrows.min()]]
    ax.imshow(zsub, extent=zext, cmap="terrain", alpha=0.85, origin="upper")
    zlevels = np.arange(np.nanmin(zsub)//10*10, np.nanmax(zsub)+10, 10)
    zcs = ax.contour(lons[zcols.min():zcols.max()+1], lats[zrows.min():zrows.max()+1], zsub,
                     levels=zlevels,
                     colors="k", linewidths=0.35, alpha=0.4)
    ax.clabel(zcs, levels=zlevels[::2], fontsize=6, fmt="%d m")
    ax.plot(ring[:, 0], ring[:, 1], color="#d62728", linewidth=2.5, label="Límite microcuenca")
    for f in cauce:
        if f.get("geometry", {}).get("type") == "LineString":
            xy = np.asarray(f["geometry"]["coordinates"])
            ax.plot(xy[:, 0], xy[:, 1], "k--", linewidth=2, label="Cauce DEM")
    for el in osm.get("elements", []):
        geom = el.get("geometry") or []
        if len(geom) < 2: continue
        xs = [p["lon"] for p in geom]; ys = [p["lat"] for p in geom]
        if max(xs) < zx0 or min(xs) > zx1 or max(ys) < zy0 or min(ys) > zy1: continue
        ax.plot(xs, ys, color="#1976d2", linewidth=1.4, alpha=0.85, label="Cauce OSM")
    ax.scatter(*station, s=90, marker="^", color="#7b2cbf", edgecolor="white", zorder=7, label="Estación")
    ax.scatter(*outlet, s=100, marker="X", color="black", edgecolor="white", zorder=8, label="Outlet")
    ax.set(xlim=(zx0, zx1), ylim=(zy0, zy1), xlabel="Longitud (°E)", ylabel="Latitud (°N)")
    ax.set_title("Detalle del outlet y la red de drenaje")
    ax.grid(alpha=0.25)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left", fontsize=8)
    fig.savefig(OUT_ZOOM, dpi=240)
    plt.close(fig)

    rows_out = []
    for name, d in sorted(set(named), key=lambda x: x[1]):
        rows_out.append({"nombre_cauce": name, "distancia_min_outlet_m": round(float(d), 2)})
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre_cauce", "distancia_min_outlet_m"])
        w.writeheader(); w.writerows(rows_out)
    print(f"Mapa: {OUT}")
    print(f"Cauces etiquetados: {len(rows_out)}")
    for row in rows_out[:8]:
        print(row)


if __name__ == "__main__":
    main()
