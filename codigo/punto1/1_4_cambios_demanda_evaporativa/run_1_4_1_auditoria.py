"""Auditoría adicional de 1.4.1: estacionalidad, dependencia y extremos.

No modifica series fuente. Usa únicamente meses completos de 1981--2022 y
produce diagnósticos de sensibilidad para FAO-56 y Thornthwaite.
"""
from pathlib import Path
from statistics import NormalDist
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DAILY = ROOT / 'datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_diaria_preliminar_90pct.csv'
MASTER = ROOT / 'datos/punto1/procesados/1_1_c_metodos_alternativos/1_1c_tabla_maestra_mensual_preliminar_90pct.csv'
OUT = ROOT / 'datos/punto1/procesados/1_4_cambios_demanda_evaporativa'
TAB = ROOT / 'productos/punto1/1_4_cambios_demanda_evaporativa/tablas'
FIG = ROOT / 'productos/punto1/1_4_cambios_demanda_evaporativa/figuras'
ANN = ROOT / 'anexos/punto1/1_4_cambios_demanda_evaporativa'
NORM = NormalDist()
MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def pnorm(z):
    return float(2 * (1 - NORM.cdf(abs(float(z)))))


def p_adjust_bh(pvalues):
    """Benjamini--Hochberg, preservando el orden original."""
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    q = np.empty(len(p), dtype=float)
    last = 1.0
    m = len(p)
    for rank in range(m, 0, -1):
        idx = order[rank - 1]
        last = min(last, p[idx] * m / rank)
        q[idx] = last
    return q


def mk_sen(y):
    """Mann--Kendall normal con corrección por empates y pendiente de Sen."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    dy = y[None, :] - y[:, None]
    iu = np.triu_indices(n, 1)
    diffs = dy[iu]
    lags = (iu[1] - iu[0]).astype(float)
    slopes = diffs / lags
    slopes.sort()
    s = float(np.sign(diffs).sum())
    _, counts = np.unique(y, return_counts=True)
    tie = np.sum(counts * (counts - 1) * (2 * counts + 5))
    var_s = float((n * (n - 1) * (2 * n + 5) - tie) / 18)
    z = (s - 1) / math.sqrt(var_s) if s > 0 else ((s + 1) / math.sqrt(var_s) if s < 0 else 0.0)
    c = 1.959963984540054 * math.sqrt(var_s)
    lo = max(0, int(math.floor((len(slopes) - c) / 2)))
    hi = min(len(slopes) - 1, int(math.ceil((len(slopes) + c) / 2)))
    return dict(n=n, S=s, var_s=var_s, z=z, p=pnorm(z), sen=float(np.median(slopes)),
                sen_ci_low=float(slopes[lo]), sen_ci_high=float(slopes[hi]))


def ols_stats(y):
    """OLS convencional y OLS HAC Newey--West con selección automática de rezago."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    x = np.arange(n, dtype=float)
    X = np.column_stack([np.ones(n), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    inv = np.linalg.inv(X.T @ X)
    sigma2 = float((resid @ resid) / (n - 2))
    se_plain = math.sqrt(float(sigma2 * inv[1, 1]))
    p_plain = pnorm(beta[1] / se_plain)
    lag = max(1, int(math.floor(4 * (n / 100) ** (2 / 9))))
    xe = X * resid[:, None]
    S = xe.T @ xe
    for ell in range(1, lag + 1):
        w = 1 - ell / (lag + 1)
        gamma = xe[ell:].T @ xe[:-ell]
        S += w * (gamma + gamma.T)
    cov_hac = inv @ S @ inv
    se_hac = math.sqrt(max(0.0, float(cov_hac[1, 1])))
    p_hac = pnorm(beta[1] / se_hac) if se_hac > 0 else float('nan')
    acf = [pd.Series(resid).autocorr(k) for k in range(1, min(6, n - 1) + 1)]
    return dict(ols_slope=float(beta[1]), ols_p=float(p_plain), ols_se=float(se_plain),
                hac_lag=lag, hac_se=float(se_hac), hac_p=float(p_hac),
                residual_lag1=float(acf[0]), residual_acf=acf, residuals=resid)


def tfpw_mk(y):
    """Trend-free prewhitening: p MK corregido; Sen se conserva en unidades originales."""
    y = np.asarray(y, dtype=float)
    raw = mk_sen(y)
    x = np.arange(len(y), dtype=float)
    detrended = y - raw['sen'] * x
    r1 = float(pd.Series(detrended).autocorr(1))
    bound = 1.959963984540054 / math.sqrt(len(y))
    if not np.isfinite(r1) or abs(r1) <= bound:
        return raw | {'detrended_lag1': r1, 'acf_bound': bound, 'tfpw_applied': False,
                      'p_tfpw': raw['p'], 'z_tfpw': raw['z']}
    prewhite = detrended[1:] - r1 * detrended[:-1] + raw['sen'] * x[1:]
    corrected = mk_sen(prewhite)
    return raw | {'detrended_lag1': r1, 'acf_bound': bound, 'tfpw_applied': True,
                  'p_tfpw': corrected['p'], 'z_tfpw': corrected['z']}


def seasonal_mk(df, value):
    """Estacional MK combinado y Sen a partir de pares dentro de cada mes calendario."""
    all_slopes, s_total, var_total = [], 0.0, 0.0
    corrected_s, corrected_var = 0.0, 0.0
    applied = 0
    for month in range(1, 13):
        y = df.loc[df.date.dt.month == month, value].to_numpy(float)
        raw = mk_sen(y)
        adj = tfpw_mk(y)
        all_slopes.extend([(y[j] - y[i]) / (j - i) for i in range(len(y)) for j in range(i + 1, len(y))])
        s_total += raw['S']; var_total += raw['var_s']
        if adj['tfpw_applied']:
            # z corregido se transforma a contribución S equivalente con la varianza original.
            corrected_s += adj['z_tfpw'] * math.sqrt(raw['var_s'])
            applied += 1
        else:
            corrected_s += raw['S']
        corrected_var += raw['var_s']
    all_slopes = np.sort(np.asarray(all_slopes, dtype=float))
    z = (s_total - 1) / math.sqrt(var_total) if s_total > 0 else ((s_total + 1) / math.sqrt(var_total) if s_total < 0 else 0.0)
    zc = corrected_s / math.sqrt(corrected_var)
    c = 1.959963984540054 * math.sqrt(var_total)
    lo = max(0, int(math.floor((len(all_slopes) - c) / 2)))
    hi = min(len(all_slopes) - 1, int(math.ceil((len(all_slopes) + c) / 2)))
    return dict(seasonal_sen=float(np.median(all_slopes)), seasonal_sen_ci_low=float(all_slopes[lo]),
                seasonal_sen_ci_high=float(all_slopes[hi]), seasonal_mk_p=pnorm(z),
                seasonal_mk_z=float(z), seasonal_mk_p_tfpw=pnorm(zc), seasonal_mk_z_tfpw=float(zc),
                months_tfpw_applied=int(applied), n_months=12)


def robustness(annual, value):
    rows = []
    years = annual.year.to_numpy(int)
    y = annual[value].to_numpy(float)
    base = mk_sen(y)
    full_ols = ols_stats(y)
    x = np.arange(len(y), dtype=float)
    # Influencia OLS: Cook's D con dos parámetros.
    X = np.column_stack([np.ones(len(y)), x])
    hat = np.sum(X * (X @ np.linalg.inv(X.T @ X)), axis=1)
    mse = np.sum(full_ols['residuals'] ** 2) / (len(y) - 2)
    cooks = full_ols['residuals'] ** 2 / (2 * mse) * hat / (1 - hat) ** 2
    threshold = 4 / len(y)

    scenarios = [('registro_completo', np.ones(len(y), dtype=bool), '')]
    for k in (1, 3, 5):
        scenarios.append((f'sin_primeros_{k}_anos', np.arange(len(y)) >= k, 'extremo_inicial'))
        scenarios.append((f'sin_ultimos_{k}_anos', np.arange(len(y)) < len(y) - k, 'extremo_final'))
    for idx, year in enumerate(years):
        mask = np.ones(len(y), dtype=bool); mask[idx] = False
        scenarios.append((f'sin_ano_{year}', mask, 'leave_one_out'))
    for name, mask, kind in scenarios:
        yy = y[mask]
        mk = mk_sen(yy); ols = ols_stats(yy)
        removed = ','.join(str(v) for v in years[~mask]) or ''
        rows.append(dict(variable=value, scenario=name, scenario_type=kind, n=len(yy),
                         period_start=int(years[mask].min()), period_end=int(years[mask].max()),
                         removed_years=removed, sen_slope_mm_yr=mk['sen'], mk_p=mk['p'],
                         ols_slope_mm_yr=ols['ols_slope'], ols_p=ols['ols_p'],
                         ols_hac_p=ols['hac_p'], sign_matches_full=bool(np.sign(mk['sen']) == np.sign(base['sen'])),
                         nominal_mk_significant=bool(mk['p'] <= .05), hac_ols_significant=bool(ols['hac_p'] <= .05)))
    influence = pd.DataFrame({'variable': value, 'year': years, 'annual_value': y,
                              'ols_residual': full_ols['residuals'], 'cooks_distance': cooks,
                              'cooks_threshold_4_over_n': threshold,
                              'influential_cooks': cooks > threshold})
    return pd.DataFrame(rows), influence


def main():
    for path in (OUT, TAB, FIG, ANN): path.mkdir(parents=True, exist_ok=True)
    daily = pd.read_csv(DAILY, parse_dates=['date'])
    daily = daily[daily.date.dt.year.between(1981, 2022)].copy()
    monthly_fao = daily.set_index('date').resample('MS').agg(fao56=('eto_fao56_mm_d', 'sum'), n_days=('eto_fao56_mm_d', 'size')).reset_index()
    expected_days = monthly_fao.date.dt.days_in_month
    assert len(monthly_fao) == 42 * 12 and (monthly_fao.n_days == expected_days).all(), 'Hay meses diarios incompletos.'
    master = pd.read_csv(MASTER, parse_dates=['date'])
    thorn = master[['date', 'thornthwaite_1948']].rename(columns={'thornthwaite_1948': 'thornthwaite'})
    monthly = monthly_fao.merge(thorn, on='date', validate='one_to_one')
    assert len(monthly) == 42 * 12 and monthly[['fao56', 'thornthwaite']].notna().all().all(), 'Falta un mes o valor.'
    monthly['year'] = monthly.date.dt.year
    annual = monthly.set_index('date')[['fao56', 'thornthwaite']].resample('YS').sum().reset_index()
    annual['year'] = annual.date.dt.year

    seasonal_rows, acf_rows, robust_frames, influence_frames = [], [], [], []
    for value, label in [('fao56', 'ETo FAO-56'), ('thornthwaite', 'Thornthwaite')]:
        p_raw, p_tfpw = [], []
        local = []
        for month in range(1, 13):
            series = monthly.loc[monthly.date.dt.month == month, value].to_numpy(float)
            result = tfpw_mk(series)
            ols = ols_stats(series)
            local.append(dict(variable=label, month_number=month, month_name=MONTHS[month-1], period='1981-2022', n=len(series),
                              sen_slope_mm_month_per_year=result['sen'], sen_ci95_low_mm_month_per_year=result['sen_ci_low'], sen_ci95_high_mm_month_per_year=result['sen_ci_high'],
                              mk_S=result['S'], mk_z=result['z'], mk_p_raw=result['p'], detrended_lag1=result['detrended_lag1'], acf_bound=result['acf_bound'],
                              tfpw_applied=result['tfpw_applied'], mk_z_tfpw=result['z_tfpw'], mk_p_tfpw=result['p_tfpw'],
                              ols_slope_mm_month_per_year=ols['ols_slope'], ols_p=ols['ols_p'], ols_hac_lag=ols['hac_lag'], ols_hac_p=ols['hac_p']))
            p_raw.append(result['p']); p_tfpw.append(result['p_tfpw'])
        q_raw, q_tfpw = p_adjust_bh(p_raw), p_adjust_bh(p_tfpw)
        for row, qr, qt in zip(local, q_raw, q_tfpw):
            row['q_fdr_bh_raw'] = qr; row['q_fdr_bh_tfpw'] = qt
            row['significant_fdr_0_05'] = bool(qt <= .05)
            seasonal_rows.append(row)
        smk = seasonal_mk(monthly, value)
        annual_ols = ols_stats(annual[value].to_numpy(float))
        acf_rows.append(dict(variable=label, scale='annual', period='1981-2022', n=42,
                             raw_lag1=float(pd.Series(annual[value]).autocorr(1)), residual_lag1=annual_ols['residual_lag1'],
                             acf_bound=1.959963984540054/math.sqrt(42), hac_lag=annual_ols['hac_lag'],
                             ols_slope_mm_yr=annual_ols['ols_slope'], ols_p=annual_ols['ols_p'], ols_hac_p=annual_ols['hac_p'], **smk))
        rb, inf = robustness(annual, value)
        rb['variable_label'] = label; inf['variable_label'] = label
        robust_frames.append(rb); influence_frames.append(inf)

    seasonal = pd.DataFrame(seasonal_rows)
    acf = pd.DataFrame(acf_rows)
    robust = pd.concat(robust_frames, ignore_index=True)
    influence = pd.concat(influence_frames, ignore_index=True)
    seasonal.to_csv(TAB/'1_4_1_tendencias_estacionales_mensuales.csv', index=False, encoding='utf-8')
    acf.to_csv(TAB/'1_4_1_autocorrelacion_y_correcciones.csv', index=False, encoding='utf-8')
    robust.to_csv(TAB/'1_4_1_robustez_extremos.csv', index=False, encoding='utf-8')
    influence.to_csv(TAB/'1_4_1_influencia_anual_cooks.csv', index=False, encoding='utf-8')

    # Figura mensual con significancia después de FDR sobre el p corregido TFPW.
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for ax, (label, color) in zip(axes, [('ETo FAO-56', '#1f77b4'), ('Thornthwaite', '#ff7f0e')]):
        z = seasonal[seasonal.variable == label]
        ax.axhline(0, color='black', linewidth=.8)
        ax.bar(z.month_number, z.sen_slope_mm_month_per_year, color=color, alpha=.82)
        sig = z.significant_fdr_0_05.to_numpy(bool)
        ax.scatter(z.month_number[sig], z.sen_slope_mm_month_per_year[sig], marker='*', color='black', s=90, label='FDR y TFPW p ≤ 0.05')
        ax.set_ylabel('Sen (mm/mes por año)'); ax.set_title(label); ax.legend(loc='best', frameon=False)
    axes[-1].set_xticks(range(1, 13), [m[:3] for m in MONTHS]); axes[-1].set_xlabel('Mes calendario')
    fig.suptitle('Racarumi: tendencias mensuales, 1981-2022')
    fig.tight_layout()
    fig.savefig(FIG/'1_4_1_tendencias_estacionales_fdr_tfpw.png', dpi=180)
    fig.savefig(FIG/'1_4_1_tendencias_estacionales_fdr_tfpw.pdf')
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, (value, label, color) in zip(axes, [('fao56', 'ETo FAO-56', '#1f77b4'), ('thornthwaite', 'Thornthwaite', '#ff7f0e')]):
        z = robust[(robust.variable == value) & (robust.scenario_type == 'leave_one_out')]
        ax.axhline(mk_sen(annual[value])['sen'], color='black', linewidth=.9, label='Registro completo')
        ax.scatter(z.period_start, z.sen_slope_mm_yr, color=color, s=20)
        ax.set_title(label); ax.set_xlabel('Año retirado'); ax.set_ylabel('Sen (mm/año por año)')
        ax.legend(frameon=False)
    fig.suptitle('Sensibilidad leave-one-out: ninguna observación se elimina de la serie fuente')
    fig.tight_layout()
    fig.savefig(FIG/'1_4_1_robustez_leave_one_out.png', dpi=180)
    fig.savefig(FIG/'1_4_1_robustez_leave_one_out.pdf')
    plt.close(fig)

    summary = {
        'period': '1981-2022', 'monthly_records': int(len(monthly)), 'annual_records': int(len(annual)),
        'source_daily': str(DAILY.relative_to(ROOT)), 'source_thornthwaite': str(MASTER.relative_to(ROOT)),
        'method': 'MK/Sen mensual, FDR BH por método, TFPW cuando |r1 detrendido| supera 1.96/sqrt(n); OLS HAC Newey-West para comparación.',
        'limits': 'Cobertura ETo 90.1264 %; el borde incompleto de 31-08-2023 no está en 1981-2022.'
    }
    pd.DataFrame([summary]).to_csv(OUT/'1_4_1_auditoria_metadatos.csv', index=False, encoding='utf-8')
    print('Auditoría 1.4.1 completada:', len(seasonal), 'filas mensuales,', len(robust), 'escenarios de robustez.')


if __name__ == '__main__':
    main()
