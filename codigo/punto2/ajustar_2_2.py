"""Inicio reproducible del apartado 2.2 con año hidrologico octubre-septiembre."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "extremos_2_2"
OUT.mkdir(exist_ok=True)
DUR = {"10min": 1, "30min": 3, "1h": 6, "3h": 18, "6h": 36, "12h": 72, "24h": 144}
TRET = [2, 5, 10, 25, 50, 100]

def require_input(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Entrada no incluida: {path.relative_to(ROOT)}")
    return path

def main():
    raw = pd.read_csv(require_input(DATA / "abtsgmuend_precipitation_10min.csv"), usecols=["timestamp_utc", "precip_mm"])
    raw["timestamp_utc"] = pd.to_datetime(raw.timestamp_utc.astype(str), format="%Y%m%d%H%M", errors="coerce")
    raw.precip_mm = pd.to_numeric(raw.precip_mm, errors="coerce")
    raw.loc[raw.precip_mm < 0, "precip_mm"] = np.nan
    s = raw.dropna(subset=["timestamp_utc"]).set_index("timestamp_utc").precip_mm.sort_index()
    s = s[~s.index.duplicated(keep="first")].asfreq("10min")
    hydro_year = np.where(s.index.month >= 10, s.index.year + 1, s.index.year)
    ams = pd.DataFrame(index=s.index)
    ams["hydro_year"] = hydro_year
    for name, win in DUR.items():
        ams[name] = s.rolling(win, min_periods=win).sum().to_numpy()
    rows = []
    for y in range(2006, 2026):
        g = ams[ams.hydro_year == y]
        row = {"hydro_year": y}
        for name in DUR:
            row[f"max_{name}_mm"] = g[name].max()
            row[f"max_{name}_timestamp_utc"] = g[name].idxmax().isoformat() if g[name].notna().any() else ""
        rows.append(row)
    annual = pd.DataFrame(rows)
    annual.to_csv(OUT / "ams_hydrological_oct_sep.csv", index=False, float_format="%.3f")

    fit_rows, q_rows = [], []
    for name in DUR:
        x = annual[f"max_{name}_mm"].dropna().to_numpy(float)
        models = {
            "gumbel_mle": (stats.gumbel_r, stats.gumbel_r.fit(x), lambda p, pars: stats.gumbel_r.ppf(p, *pars)),
            "gev_mle": (stats.genextreme, stats.genextreme.fit(x), lambda p, pars: stats.genextreme.ppf(p, *pars)),
        }
        # Log-Pearson III se ajusta en log10; los cuantiles se devuelven en mm.
        lx = np.log10(x)
        lp_pars = stats.pearson3.fit(lx)
        models["logpearson3_mle"] = (stats.pearson3, lp_pars, lambda p, pars: 10 ** stats.pearson3.ppf(p, *pars))
        for model, (dist, pars, qfun) in models.items():
            if model == "logpearson3_mle":
                fitted = dist.cdf(lx, *pars)
                ks = stats.kstest(lx, lambda z: dist.cdf(z, *pars))
            else:
                fitted = dist.cdf(x, *pars)
                ks = stats.kstest(x, lambda z: dist.cdf(z, *pars))
            fit_rows.append({"duration": name, "model": model, "n": len(x), "ks_stat": ks.statistic,
                             "ks_pvalue": ks.pvalue, "parameters": ";".join(f"{v:.8g}" for v in pars)})
            for T in TRET:
                p = 1 - 1 / T
                q_rows.append({"duration": name, "model": model, "T_years": T, "quantile_mm": float(qfun(p, pars)),
                               "intensity_mm_h": float(qfun(p, pars) / (sum(DUR[name] for _ in [0]) / 6))})
    pd.DataFrame(fit_rows).to_csv(OUT / "fit_summary_mle.csv", index=False)
    pd.DataFrame(q_rows).to_csv(OUT / "quantiles_mle.csv", index=False, float_format="%.4f")
    # Kendall/Sen sobre el año hidrologico para el requisito de estacionariedad.
    trend = []
    for name in DUR:
        x = annual[f"max_{name}_mm"].to_numpy(float)
        tau, p = stats.kendalltau(annual.hydro_year, x)
        sen = stats.theilslopes(x, annual.hydro_year)
        trend.append({"duration": name, "kendall_tau": tau, "kendall_pvalue": p,
                      "sen_slope_mm_per_year": sen.slope, "sen_low95": sen.low_slope, "sen_high95": sen.high_slope})
    pd.DataFrame(trend).to_csv(OUT / "stationarity_hydrological_year.csv", index=False, float_format="%.6f")
    print(f"AMS hidrologica: {len(annual)} años; ajustes MLE: {len(fit_rows)}")

if __name__ == "__main__":
    main()
