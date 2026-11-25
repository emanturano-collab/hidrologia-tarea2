"""Contraste del evento del 24/07/2013 con estaciones vecinas y radar (control 2.1.5).

Lee datos/punto2/vecinas_2013/ (preparados por descargar_vecinas_2013.py) y la serie
principal de la estacion 00020. Escribe en productos/punto2/final/:
  - tablas/evento_2013_estaciones.csv, tablas/vecinas_requisitos.csv, tablas/vecinas_ams_1h.csv
  - figuras/evento_2013_contraste.png
  - cifras_evento2013.tex (macros LaTeX para el informe)

Ejecucion: python codigo/punto2/contraste_evento_2013.py
"""
from pathlib import Path
import math

import numpy as np
import pandas as pd
from scipy import optimize, stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lmoments3 import distr

ROOT = Path(__file__).resolve().parents[2]
VEC = ROOT / "datos" / "punto2" / "vecinas_2013"
PROPIA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen" / "abtsgmuend_precipitation_10min.csv"
OUT = ROOT / "productos" / "punto2" / "final"
LAT0, LON0 = 48.9219, 9.9129
R_TIERRA, PHI_TS, LAM_0 = 6370.04, math.radians(60.0), math.radians(10.0)
DIA = "2013-07-24"


def km(lat, lon):
    dl, dn = math.radians(lat - LAT0), math.radians(lon - LON0)
    a = math.sin(dl / 2) ** 2 + math.cos(math.radians(LAT0)) * math.cos(math.radians(lat)) * math.sin(dn / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def radolan_xy(lat, lon):
    """Proyeccion estereografica polar de RADOLAN (km)."""
    phi, lam = math.radians(lat), math.radians(lon)
    m = (1 + math.sin(PHI_TS)) / (1 + math.sin(phi))
    return (R_TIERRA * m * math.cos(phi) * math.sin(lam - LAM_0),
            -R_TIERRA * m * math.cos(phi) * math.cos(lam - LAM_0))


def leer_asc(f):
    with open(f) as fh:
        hd = {k: float(v) for k, v in (next(fh).split() for _ in range(6))}
        z = np.loadtxt(fh)
    return np.where(z < 0, np.nan, z / 10.0)[::-1], hd  # decimas de mm -> mm; fila 0 = sur


def serie10(sid):
    if sid == "00020":
        d = pd.read_csv(PROPIA, usecols=["timestamp_utc", "precip_mm"]).rename(columns={"timestamp_utc": "fecha_utc"})
    else:
        d = pd.read_csv(VEC / f"10min_{sid}.csv")
    x = d.set_index(pd.to_datetime(d["fecha_utc"].astype(str), format="%Y%m%d%H%M"))["precip_mm"].astype(float)
    return x.where(x >= 0)


def gev_gmle(x):
    """GEV por maxima verosimilitud generalizada (Martins y Stedinger, 2000), convencion de scipy."""
    p0 = distr.gev.lmom_fit(x)
    def nlp(v):
        c, loc, lsc = v
        if not -0.5 < c < 0.5:
            return np.inf
        ll = stats.genextreme.logpdf(x, c, loc, np.exp(lsc)).sum()
        return -(ll + stats.beta.logpdf(c + 0.5, 6, 9)) if np.isfinite(ll) else np.inf
    s = optimize.minimize(nlp, [np.clip(p0["c"], -0.45, 0.45), p0["loc"], np.log(p0["scale"])], method="Nelder-Mead")
    return s.x[0], s.x[1], float(np.exp(s.x[2]))


est = pd.read_csv(VEC / "estaciones.csv", dtype={"id": str})
est["id"] = est["id"].str.zfill(5)
coords = est.drop_duplicates("id").set_index("id")
coords.loc["00020", ["lat", "lon", "nombre", "altura_m"]] = [LAT0, LON0, "Abtsgmund-Untergroningen", 432]

# Radar: suma 11:50-14:50 UTC y maxima horaria en la celda de cada estacion
campos, hd = zip(*[leer_asc(VEC / f"radolan_RW_20130724-{h}.asc") for h in ("1250", "1350", "1450")])
hd = hd[0]
r3, r1 = np.nansum(campos, axis=0), np.nanmax(campos, axis=0)


def celda(lat, lon):
    x, y = radolan_xy(lat, lon)
    return int((y - hd["yllcorner"] / 1000) // 1), int((x - hd["xllcorner"] / 1000) // 1)


diaria = pd.read_csv(VEC / "diaria_20130720_20130728.csv", dtype={"STATIONS_ID": str})
diaria["id"] = diaria["STATIONS_ID"].str.zfill(5)
d24 = diaria[diaria["MESS_DATUM"] == 20130724].set_index("id")["RS"]

filas = []
ids10 = ["00020", "06262", "01197", "01538", "02485"]
for sid in sorted(set(coords.index) | set(ids10)):
    c = coords.loc[sid]
    i, j = celda(c.lat, c.lon)
    fila = {"id": sid, "nombre": c.nombre, "distancia_km": km(c.lat, c.lon), "altura_m": c.altura_m,
            "lluvia_diaria_mm": d24.get(sid, np.nan), "radar_3h_mm": r3[i, j], "radar_max1h_mm": r1[i, j]}
    if sid in ids10:
        x = serie10(sid).loc["2013-07-23":"2013-07-25"]
        fila |= {"max10min_mm": x.loc[DIA].max(), "max1h_mm": x.rolling(6).sum().loc[DIA].max(),
                 "hora_max10_utc": x.loc[DIA].idxmax().strftime("%H:%M"), "total_dia_10min_mm": x.loc[DIA].sum()}
    filas.append(fila)
ev = pd.DataFrame(filas).sort_values("distancia_km")
ev.to_csv(OUT / "tablas" / "evento_2013_estaciones.csv", index=False, float_format="%.2f")

# Requisitos de 2.1 y maximos anuales de 1 h para las vecinas con registro largo
req, ams = [], {}
for sid in ["00020", "06262", "01197"]:
    x = serie10(sid)
    x = x.reindex(pd.date_range(x.index.min().floor("D"), x.index.max(), freq="10min"))
    hy = x.index.year + (x.index.month >= 10)
    comp = x.notna().groupby(hy).mean() * 100
    verano = x[(x.index.month >= 5) & (x.index.month <= 9)]
    comp_v = verano.notna().groupby(verano.index.year).mean() * 100
    anios = [a for a in comp.index if x.index.min().year < a <= 2025 and comp[a] >= 80 and comp_v.get(a, 0) >= 90]
    m1 = x.rolling(6, min_periods=6).sum().groupby(hy).max().reindex(anios) * 1 / (1 - 1 / 48)  # Weiss n = 6
    ams[sid] = m1
    c, loc, sc = gev_gmle(m1.values)
    q = lambda T: stats.genextreme.ppf(1 - 1 / T, c, loc, sc)
    req.append({"id": sid, "nombre": coords.loc[sid, "nombre"], "resolucion_min": 10, "anios_validos": len(anios),
                "primer_anio": min(anios), "ultimo_anio": max(anios), "completitud_min_pct": comp.reindex(anios).min(),
                "ams1h_mediana_mm": m1.median(), "ams1h_max_mm": m1.max(), "anio_max": int(m1.idxmax()),
                "q25_1h_mm": q(25), "q100_1h_mm": q(100), "forma_c": c,
                "cumple_2_1": len(anios) >= 20})
req = pd.DataFrame(req)
req.to_csv(OUT / "tablas" / "vecinas_requisitos.csv", index=False, float_format="%.3f")
amsdf = pd.DataFrame(ams)
amsdf.to_csv(OUT / "tablas" / "vecinas_ams_1h.csv", float_format="%.2f")
rho = amsdf.dropna().corr(method="spearman")

# Figura
fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1, 1.2]})
ext = np.array([hd["xllcorner"], hd["xllcorner"] + 81 * hd["cellsize"], hd["yllcorner"], hd["yllcorner"] + 81 * hd["cellsize"]]) / 1000
im = axs[0].imshow(r3, origin="lower", extent=ext, cmap="Blues", vmin=0)
plt.colorbar(im, ax=axs[0], label="Lluvia radar 11:50-14:50 UTC (mm)")
for sid, c in coords.iterrows():
    x, y = radolan_xy(c.lat, c.lon)
    axs[0].plot(x, y, "r^" if sid == "00020" else "ko", ms=6 if sid == "00020" else 4)
    lab = f"{d24.get(sid, np.nan):.0f}" if sid in d24.index else ""
    axs[0].annotate(lab, (x, y), xytext=(3, 3), textcoords="offset points", fontsize=7)
axs[0].set(xlabel="x RADOLAN (km)", ylabel="y RADOLAN (km)", title="Radar (color) y pluviómetros (mm/día)")
for sid, col in (("00020", "crimson"), ("06262", "tab:blue"), ("01197", "tab:green")):
    x = serie10(sid).loc[f"{DIA} 11:00":f"{DIA} 15:00"]
    axs[1].step(x.index, x.values, where="post", color=col, label=f"{coords.loc[sid, 'nombre']} ({km(coords.loc[sid].lat, coords.loc[sid].lon):.0f} km)")
axs[1].set(ylabel="Lluvia en 10 min (mm)", title="24/07/2013, hora UTC")
axs[1].xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
axs[1].legend(fontsize=7)
fig.tight_layout()
fig.savefig(OUT / "figuras" / "evento_2013_contraste.png", dpi=150)
plt.close(fig)


# Macros LaTeX
def f(v, nd):
    return f"{v:.{nd}f}".replace(".", "{,}")


e = ev.set_index("id")
rq = req.set_index("id")
m = {
    "EvRadarEst": f(e.loc["00020", "radar_max1h_mm"], 1), "EvRadarTresEst": f(e.loc["00020", "radar_3h_mm"], 1),
    "EvRadarMaxVent": f(np.nanmax(r3), 1), "EvAreaCuarenta": str(int((r3 > 40).sum())),
    "EvBuhler": f(e.loc["00774", "lluvia_diaria_mm"], 1), "EvNeubronn": f(e.loc["00019", "lluvia_diaria_mm"], 1),
    "EvGoggingen": f(e.loc["01674", "lluvia_diaria_mm"], 1), "EvAalen": f(e.loc["00006", "lluvia_diaria_mm"], 1),
    "EvHeubach": f(e.loc["02194", "lluvia_diaria_mm"], 1),
    "EvGmundHora": f(e.loc["06262", "max1h_mm"], 1), "EvEllwHora": f(e.loc["01197", "max1h_mm"], 1),
    "EvGmundDia": f(e.loc["06262", "total_dia_10min_mm"], 1), "EvGmundKm": f(e.loc["06262", "distancia_km"], 0),
    "EvEllwKm": f(e.loc["01197", "distancia_km"], 0), "EvBuhlerKm": f(e.loc["00774", "distancia_km"], 0),
    "EvRadarBuhler": f(e.loc["00774", "radar_max1h_mm"], 1),
    "VecGmundAnios": str(rq.loc["06262", "anios_validos"]), "VecEllwAnios": str(rq.loc["01197", "anios_validos"]),
    "VecGmundComp": f(rq.loc["06262", "completitud_min_pct"], 1), "VecEllwComp": f(rq.loc["01197", "completitud_min_pct"], 1),
    "VecGmundQcien": f(rq.loc["06262", "q100_1h_mm"], 1), "VecEllwQcien": f(rq.loc["01197", "q100_1h_mm"], 1),
    "VecPropQcien": f(rq.loc["00020", "q100_1h_mm"], 1),
    "VecRhoGmund": f(rho.loc["00020", "06262"], 2), "VecRhoEllw": f(rho.loc["00020", "01197"], 2),
}
(OUT / "cifras_evento2013.tex").write_text("% Generado por codigo/punto2/contraste_evento_2013.py\n"
                                           + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()) + "\n", encoding="utf-8")
print(ev.round(1).to_string(index=False))
print(req.round(2).to_string(index=False))
print(rho.round(2))
