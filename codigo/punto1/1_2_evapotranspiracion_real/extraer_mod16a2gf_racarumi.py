"""Extrae ET MOD16A2GF sobre Racarumi como tablas, sin exportar rasteres.

ET es un acumulado por compuesto y se reparte de forma uniforme entre los
dias de solapamiento con cada mes. ET_QC se resume, pero no se usa para
enmascarar ET: solo se excluyen los codigos fill documentados (>=32761).
"""
from __future__ import annotations

import json
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import ee
import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
GPKG = ROOT / "datos" / "punto1" / "PE_200907_catchment_T1_original.gpkg"
RAW = ROOT / "datos" / "punto1" / "mod16a2gf_racarumi_composites_raw.csv"
OUT = ROOT / "productos" / "punto1"
COLLECTION = "MODIS/061/MOD16A2GF"
PROJECT = "hidrologia-racarumi"
TARGET_WINDOWS = [(date(2001, 9, 1), date(2002, 9, 1)),
                  (date(2003, 9, 1), date(2023, 9, 1))]


def retry(call, attempts=4):
    err = None
    for i in range(attempts):
        try:
            return call()
        except Exception as exc:  # Earth Engine transient errors
            err = exc
            if i + 1 < attempts:
                time.sleep(3 * (i + 1))
    raise err


def intervals():
    """Return contiguous required daily windows, without the AH 2003 gap."""
    for start, end in TARGET_WINDOWS:
        d = start
        while d < end:
            next_month = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
            yield d, min(next_month, end)
            d = next_month


def hydrological_year(d: date) -> int:
    return d.year + 1 if d.month >= 9 else d.year


def load_basin():
    gdf = gpd.read_file(GPKG)
    if gdf.empty:
        raise ValueError("La delimitacion original esta vacia")
    if gdf.crs is None:
        raise ValueError("La delimitacion original no tiene CRS")
    gdf = gdf.to_crs(4326)
    geom = gdf.geometry.union_all()
    if geom.is_empty or not geom.is_valid:
        raise ValueError("Geometria original invalida")
    return ee.Geometry(mapping(geom)), geom


def fetch_composites(basin):
    # Nueve dias de guarda capturan los compuestos que cruzan los limites.
    start = min(s for s, _ in TARGET_WINDOWS) - timedelta(days=9)
    end = max(e for _, e in TARGET_WINDOWS) + timedelta(days=9)
    coll = ee.ImageCollection(COLLECTION).filterDate(start.isoformat(), end.isoformat())
    rows = []
    for info in retry(lambda: coll.aggregate_array("system:time_start").getInfo()):
        rows.append({"start": datetime.fromtimestamp(info / 1000, UTC).date()})
    rows.sort(key=lambda x: x["start"])
    if not rows:
        raise ValueError("MOD16A2GF no devolvio compuestos para el periodo requerido")
    # MODIS especifica 8 dias; la duracion final se determina con el siguiente
    # inicio. Para el ultimo se pide una imagen posterior mediante la guarda.
    for i, row in enumerate(rows[:-1]):
        row["end"] = rows[i + 1]["start"]
    rows[-1]["end"] = rows[-1]["start"] + timedelta(days=8)
    usable = []
    for row in rows:
        if any(row["start"] < e and row["end"] > s for s, e in TARGET_WINDOWS):
            usable.append(row)
    previous = pd.read_csv(RAW) if RAW.exists() else pd.DataFrame()
    done = set(previous.image_start) if not previous.empty else set()
    metadata = {r["start"].isoformat(): r for r in usable}
    todo = [r for r in usable if r["start"].isoformat() not in done]
    # Se reducen lotes de 24 imagenes en el servidor. Cada respuesta contiene
    # solo escalares; evita 968 llamadas HTTP y tambien rasteres exportados.
    for pos in range(0, len(todo), 24):
        batch = todo[pos:pos + 24]
        stamps = [int(datetime(r["start"].year, r["start"].month, r["start"].day, tzinfo=UTC).timestamp() * 1000) for r in batch]
        def reduce_one(ms):
            image = ee.Image(coll.filter(ee.Filter.eq("system:time_start", ms)).first())
            raw = image.select("ET")
            valid = raw.lt(32761)
            area = ee.Image.pixelArea()
            kwargs = {"reducer": ee.Reducer.sum(), "geometry": basin, "crs": raw.projection(),
                      "scale": 500, "maxPixels": 10**9, "bestEffort": False}
            va = area.updateMask(valid).reduceRegion(**kwargs).get("area")
            ta = area.reduceRegion(**kwargs).get("area")
            weighted = raw.updateMask(valid).multiply(0.1).multiply(area).reduceRegion(**kwargs).get("ET")
            qa = image.select("ET_QC").bitwiseAnd(1).eq(0).multiply(area).reduceRegion(**kwargs).get("ET_QC")
            return ee.Feature(None, {"time_start": ms, "valid_area_m2": va, "total_area_m2": ta,
                                     "weighted_mm_m2": weighted, "qc_good_area_m2": qa})
        fc = ee.FeatureCollection(ee.List(stamps).map(reduce_one))
        features = retry(lambda: fc.getInfo())["features"]
        rows = []
        for feat in features:
            v = feat["properties"]
            start_date = datetime.fromtimestamp(v["time_start"] / 1000, UTC).date().isoformat()
            va, ta, w, qa = (v.get(k) for k in ("valid_area_m2", "total_area_m2", "weighted_mm_m2", "qc_good_area_m2"))
            if None in (va, ta, w, qa) or ta <= 0 or va <= 0:
                raise ValueError(f"{start_date}: reduccion espacial sin datos validos")
            coverage = va / ta * 100
            if coverage < 95:
                raise ValueError(f"{start_date}: cobertura valida {coverage:.3f}% menor a 95%")
            m = metadata[start_date]
            rows.append({"image_start": start_date, "image_end": m["end"].isoformat(),
                         "duration_days": (m["end"] - m["start"]).days, "et_mm_composite": w / va,
                         "valid_area_m2": va, "total_area_m2": ta, "valid_coverage_percent": coverage,
                         "qc_modland_good_percent": qa / ta * 100, "et_scale_factor": 0.1, "source": COLLECTION})
        pd.DataFrame(rows).to_csv(RAW, mode="a", header=not RAW.exists(), index=False)
        print(f"guardado {min(pos + len(batch), len(todo))}/{len(todo)} compuestos pendientes")
    return pd.read_csv(RAW).sort_values("image_start").reset_index(drop=True)


def aggregate_months(comp):
    records = []
    for _, r in comp.iterrows():
        a, b = date.fromisoformat(r.image_start), date.fromisoformat(r.image_end)
        for s, e in intervals():
            left, right = max(a, s), min(b, e)
            if left < right:
                days = (right - left).days
                records.append({"month": s.isoformat(), "hydrological_year": hydrological_year(s),
                                "days_covered": days, "et_mm": r.et_mm_composite * days / r.duration_days,
                                "min_composite_coverage_percent": r.valid_coverage_percent})
    p = pd.DataFrame(records)
    monthly = p.groupby(["month", "hydrological_year"], as_index=False).agg(
        days_covered=("days_covered", "sum"), et_mm=("et_mm", "sum"),
        min_composite_coverage_percent=("min_composite_coverage_percent", "min"))
    monthly["expected_days"] = pd.to_datetime(monthly.month).dt.days_in_month
    if not (monthly.days_covered == monthly.expected_days).all() or len(monthly) != 252:
        bad = monthly.loc[monthly.days_covered != monthly.expected_days, ["month", "days_covered", "expected_days"]]
        raise ValueError(f"Cobertura mensual incompleta o numero de meses inesperado: {bad.to_dict('records')}")
    annual = monthly.groupby("hydrological_year", as_index=False).agg(
        months=("month", "count"), et_mod16_mm_year=("et_mm", "sum"),
        min_composite_coverage_percent=("min_composite_coverage_percent", "min"))
    if len(annual) != 21 or not (annual.months == 12).all():
        raise ValueError("No se obtuvieron exactamente los 21 anos hidrologicos completos")
    return monthly, annual


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # La renovacion OAuth puede sufrir cierres transitorios de transporte.
    retry(lambda: ee.Initialize(project=PROJECT), attempts=3)
    basin, _ = load_basin()
    comp = fetch_composites(basin)
    comp.to_csv(RAW, index=False)
    monthly, annual = aggregate_months(comp)
    monthly.to_csv(OUT / "punto_1_2_4_mod16_et_mensual.csv", index=False)
    annual.to_csv(OUT / "punto_1_2_4_mod16_et_anual_hidrologico.csv", index=False)
    summary = {"collection": COLLECTION, "project": PROJECT, "et_units": "mm por compuesto; convertido a mm/mes y mm/ano",
               "scale_factor": 0.1, "allocation": "uniforme por dia dentro de cada compuesto", "months": int(len(monthly)),
               "hydrological_years": annual.hydrological_year.tolist(), "mean_et_mm_year": annual.et_mod16_mm_year.mean(),
               "minimum_valid_coverage_percent": float(comp.valid_coverage_percent.min())}
    (OUT / "punto_1_2_4_mod16_control_calidad.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
