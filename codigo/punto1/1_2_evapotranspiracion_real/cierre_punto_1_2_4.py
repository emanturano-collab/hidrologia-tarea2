"""Genera figuras y tablas finales del numeral 1.2.4 sin alterar insumos."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
PROD = ROOT / "productos" / "punto1"
FIG = PROD / "figuras"
FIG.mkdir(parents=True, exist_ok=True)

annual = pd.read_csv(PROD / "punto_1_2_4_comparacion_anual_productos_y_balance.csv")
gm = pd.read_csv(PROD / "punto_1_2_4_gleam_et_mensual.csv")
mm = pd.read_csv(PROD / "punto_1_2_4_mod16_et_mensual.csv")
expected = [2002] + list(range(2004, 2024))
if annual.hydrological_year.tolist() != expected or len(annual) != 21:
    raise ValueError("La tabla anual no contiene exactamente AH2002 y AH2004--AH2023")
monthly = gm[["month", "et_gleam_mm_month"]].merge(
    mm[["month", "et_mm"]].rename(columns={"et_mm": "et_mod16_mm_month"}),
    on="month", validate="one_to_one")
if len(monthly) != 252 or monthly.month.nunique() != 252:
    raise ValueError("Las series mensuales no coinciden en exactamente 252 meses")

series = {
    "GLEAM4.3a": "et_gleam_mm_year",
    "MOD16A2GF v6.1": "et_mod16_mm_year",
    "PISCOp − Q": "et_l_mm_year",
    "IMERG − Q": "et_i_mm_year",
}
stats = []
for label, col in series.items():
    x = annual[col]
    stats.append({"series": label, "n_years": len(x), "mean_mm_year": x.mean(),
                  "standard_deviation_mm_year": x.std(ddof=1),
                  "minimum_mm_year": x.min(), "maximum_mm_year": x.max()})
stats = pd.DataFrame(stats)
stats.to_csv(PROD / "punto_1_2_4_estadisticos_anuales.csv", index=False)

diffs = []
labels = list(series)
for i, a in enumerate(labels):
    for b in labels[i + 1:]:
        xa, xb = annual[series[a]], annual[series[b]]
        ma, mb = xa.mean(), xb.mean()
        diffs.append({"method_a": a, "method_b_reference": b,
                      "mean_a_mm_year": ma, "mean_b_mm_year": mb,
                      "signed_difference_a_minus_b_mm_year": ma - mb,
                      "absolute_difference_between_means_mm_year": abs(ma - mb),
                      "percent_difference_relative_to_b": abs(ma - mb) / abs(mb) * 100,
                      "mean_absolute_paired_annual_difference_mm_year": np.mean(np.abs(xa - xb))})
pd.DataFrame(diffs).to_csv(PROD / "punto_1_2_4_diferencias_entre_metodos.csv", index=False)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titlesize": 13, "axes.labelsize": 11,
                     "legend.fontsize": 9})
colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
markers = ["o", "s", "^", "D"]
fig, ax = plt.subplots(figsize=(11, 6.1), constrained_layout=True)
x = np.arange(len(annual))
for (label, col), color, marker in zip(series.items(), colors, markers):
    ax.plot(x, annual[col], label=label, color=color, marker=marker,
            linewidth=1.8, markersize=4.5)
ax.axhline(0, color="#666666", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels([f"AH{y}" for y in expected], rotation=45, ha="right")
ax.set_ylabel("ET o balance P − Q (mm/año)")
ax.set_xlabel("Año hidrológico (septiembre–agosto)")
ax.set_title("Evapotranspiración anual y balances hídricos en Racarumi")
ax.grid(True, axis="y", color="#D9D9D9", linewidth=0.7)
ax.legend(ncol=2, frameon=True)
for ext in ("png", "svg"):
    fig.savefig(FIG / f"punto_1_2_4_series_anuales.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

monthly["month_number"] = pd.to_datetime(monthly.month).dt.month
clim = monthly.groupby("month_number", as_index=False).agg(
    gleam_mean=("et_gleam_mm_month", "mean"),
    gleam_sd=("et_gleam_mm_month", lambda x: x.std(ddof=1)),
    mod16_mean=("et_mod16_mm_month", "mean"),
    mod16_sd=("et_mod16_mm_month", lambda x: x.std(ddof=1)),
    n=("month", "count"))
if len(clim) != 12 or not (clim.n == 21).all():
    raise ValueError("La climatologia no tiene 12 meses con 21 observaciones cada uno")
clim.to_csv(PROD / "punto_1_2_4_climatologia_mensual_gleam_mod16.csv", index=False)
months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
fig, ax = plt.subplots(figsize=(9.6, 5.7), constrained_layout=True)
xx = np.arange(1, 13)
ax.plot(xx, clim.gleam_mean, color=colors[0], marker="o", linewidth=2, label="GLEAM4.3a")
ax.fill_between(xx, clim.gleam_mean - clim.gleam_sd, clim.gleam_mean + clim.gleam_sd,
                color=colors[0], alpha=0.13, linewidth=0)
ax.plot(xx, clim.mod16_mean, color=colors[1], marker="s", linewidth=2, label="MOD16A2GF v6.1")
ax.fill_between(xx, clim.mod16_mean - clim.mod16_sd, clim.mod16_mean + clim.mod16_sd,
                color=colors[1], alpha=0.13, linewidth=0)
ax.set_xticks(xx, months)
ax.set_ylim(bottom=0)
ax.set_ylabel("Evapotranspiración (mm/mes)")
ax.set_xlabel("Mes calendario")
ax.set_title("Climatología mensual de evapotranspiración en Racarumi")
ax.grid(True, axis="y", color="#D9D9D9", linewidth=0.7)
ax.legend(frameon=True)
ax.text(0.01, 0.02, "Línea: promedio mensual; banda: ±1 desviación estándar (n = 21 por mes)",
        transform=ax.transAxes, fontsize=8.5, color="#555555")
for ext in ("png", "svg"):
    fig.savefig(FIG / f"punto_1_2_4_climatologia_mensual.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

print(stats.to_json(orient="records", force_ascii=True, indent=2))
print(clim.to_json(orient="records", force_ascii=True, indent=2))
