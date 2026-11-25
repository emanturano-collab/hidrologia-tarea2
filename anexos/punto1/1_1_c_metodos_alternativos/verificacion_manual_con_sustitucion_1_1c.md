# Verificación manual con sustitución numérica

## Día 1981-01-01 — celda ERA5L_10
* Hargreaves–Samani: `0.0023 × (20.750021+17.8) × sqrt(27.684167−14.537256) × 15.627801 = 5.024145 mm/d`.
* Priestley–Taylor: `1.26 × 0.150718/(0.150718+0.062025) × 15.159060/lambda(T)` = `5.518622 mm/d` (pyet; G=0).
* Makkink: `0.65 × 0.150718/(0.150718+0.062025) × 26.373704/lambda(T)` = `4.953046 mm/d` (pyet).
* Meyer: `0.36 × (es(Taire)−ea) × (1+u10/16)` con `es=2.449073 kPa`, `ea=1.649168 kPa`, `u10=5.561110 km/h`, tras convertir presiones a mm Hg = `2.910644 mm/d`.
* Rohwer: con `P=699.588208 mm Hg`, `u0.6=3.720588 km/h`, y el mismo déficit de vapor convertido a mm Hg = `3.141638 mm/d`.

## Mes 1981-01-01 — Thornthwaite, celda ERA5L_02
`I=54.434898`, `a=1.348281`, `N=12.332678 h`, `d=31`. Sustitución: `16(10T/I)^a(N/12)(d/30) = 56.143626 mm/mes`. Las entradas de temperatura mensual se mantienen en `1_1c_series_mensuales_por_celda_preliminar_90pct.csv`.
