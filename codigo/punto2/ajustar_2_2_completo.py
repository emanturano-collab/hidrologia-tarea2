"""Completa 2.2: momentos, L-momentos, MLE, pruebas y bootstrap."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats, optimize
from lmoments3 import distr

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
INP = DATA / "extremos_2_2" / "ams_hydrological_oct_sep.csv"
OUT = DATA / "extremos_2_2"
DUR = {"10min": 1, "30min": 3, "1h": 6, "3h": 18, "6h": 36, "12h": 72, "24h": 144}
TS = [2, 5, 10, 25, 50, 100]
GAMMA = 0.5772156649015329

def mom_fit(name, x):
    if name == "gumbel":
        return (np.std(x, ddof=1) * np.sqrt(6) / np.pi, np.mean(x) - GAMMA * np.std(x, ddof=1) * np.sqrt(6) / np.pi)
    if name == "gev":
        m, v, sk = np.mean(x), np.var(x, ddof=1), stats.skew(x, bias=False)
        init = stats.genextreme.fit(x)
        def fun(p):
            c, loc, scale = p
            if scale <= 0: return [1e6, 1e6, 1e6]
            mm, vv, ss = stats.genextreme.stats(c, loc=loc, scale=scale, moments="mvs")
            vals = np.array([mm, vv, ss], dtype=float)
            if not np.all(np.isfinite(vals)): return [1e6, 1e6, 1e6]
            return [(mm-m)/max(abs(m),1), (vv-v)/max(v,1), (ss-sk)/max(abs(sk),1)]
        try:
            res = optimize.least_squares(fun, init, bounds=([-2, -np.inf, 1e-6], [2, np.inf, np.inf]), max_nfev=2000)
            return tuple(res.x)
        except ValueError:
            return tuple(init)
    # log-Pearson III: match the first three moments in log10-space.
    lx = np.log10(x); m, v, sk = np.mean(lx), np.var(lx, ddof=1), stats.skew(lx, bias=False)
    init = stats.pearson3.fit(lx)
    def fun(p):
        skew, loc, scale = p
        if scale <= 0: return [1e6, 1e6, 1e6]
        mm, vv, ss = stats.pearson3.stats(skew, loc=loc, scale=scale, moments="mvs")
        vals = np.array([mm, vv, ss], dtype=float)
        if not np.all(np.isfinite(vals)): return [1e6, 1e6, 1e6]
        return [(mm-m), (vv-v)/max(v,1), (ss-sk)]
    try:
        res = optimize.least_squares(fun, init, bounds=([-20, -np.inf, 1e-6], [20, np.inf, np.inf]), max_nfev=2000)
        return tuple(res.x)
    except ValueError:
        return tuple(init)

def fit(name, method, x):
    if name == "gumbel":
        if method == "mle": return tuple(stats.gumbel_r.fit(x))
        if method == "mom":
            scale, loc = mom_fit(name, x); return (loc, scale)
        return tuple(distr.gum.lmom_fit(x).values())
    if name == "gev":
        if method == "mle": return tuple(stats.genextreme.fit(x))
        if method == "mom": return mom_fit(name, x)
        return tuple(distr.gev.lmom_fit(x).values())
    lx = np.log10(x)
    if method == "mle": return tuple(stats.pearson3.fit(lx))
    if method == "mom": return mom_fit(name, x)
    return tuple(distr.pe3.lmom_fit(lx).values())

def quantile(name, pars, p):
    if name == "gumbel": return stats.gumbel_r.ppf(p, *pars)
    if name == "gev": return stats.genextreme.ppf(p, *pars)
    return 10 ** stats.pearson3.ppf(p, *pars)

def cdf(name, pars, x):
    if name == "gumbel": return stats.gumbel_r.cdf(x, *pars)
    if name == "gev": return stats.genextreme.cdf(x, *pars)
    return stats.pearson3.cdf(np.log10(x), *pars)

def main():
    annual = pd.read_csv(INP)
    fit_rows, q_rows = [], []
    for duration, win in DUR.items():
        x = annual[f"max_{duration}_mm"].dropna().to_numpy(float)
        for name in ["gumbel", "gev", "logpearson3"]:
            for method in ["mom", "lmom", "mle"]:
                pars = fit(name, method, x)
                ks = stats.kstest(x, lambda z: cdf(name, pars, z))
                cvm = stats.cramervonmises(x, lambda z: cdf(name, pars, z))
                fit_rows.append({"duration": duration, "distribution": name, "method": method,
                                 "n": len(x), "ks_stat": ks.statistic, "ks_pvalue": ks.pvalue,
                                 "cvm_stat": cvm.statistic, "cvm_pvalue": cvm.pvalue,
                                 "parameters": ";".join(f"{v:.10g}" for v in pars)})
                for T in TS:
                    val = float(quantile(name, pars, 1 - 1/T))
                    q_rows.append({"duration": duration, "distribution": name, "method": method,
                                   "T_years": T, "quantile_mm": val,
                                   "intensity_mm_h": val / (win/6)})
    pd.DataFrame(fit_rows).to_csv(OUT / "fit_summary_3methods.csv", index=False, float_format="%.8f")
    pd.DataFrame(q_rows).to_csv(OUT / "quantiles_3methods.csv", index=False, float_format="%.5f")

    # Bootstrap de cuantiles para GEV-MLE (modelo de referencia transparente).
    rng = np.random.default_rng(202602)
    boot = []
    for duration, win in DUR.items():
        x = annual[f"max_{duration}_mm"].dropna().to_numpy(float)
        for b in range(100):
            xb = rng.choice(x, size=len(x), replace=True)
            pars = stats.genextreme.fit(xb)
            for T in TS:
                val = float(stats.genextreme.ppf(1-1/T, *pars))
                boot.append({"duration": duration, "bootstrap": b, "T_years": T,
                             "quantile_mm": val, "intensity_mm_h": val/(win/6)})
    bd = pd.DataFrame(boot)
    ci = bd.groupby(["duration", "T_years"]).quantile_mm.agg(q025=lambda z: z.quantile(.025), median="median", q975=lambda z: z.quantile(.975)).reset_index()
    ci.to_csv(OUT / "bootstrap_ci_gev.csv", index=False, float_format="%.5f")
    ci["relative_width"] = (ci.q975-ci.q025)/ci["median"]
    ci.to_csv(OUT / "bootstrap_ci_gev.csv", index=False, float_format="%.5f")
    print(f"Ajustes: {len(fit_rows)}; cuantiles bootstrap: {len(ci)}")

if __name__ == "__main__":
    main()
