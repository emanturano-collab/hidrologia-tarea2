# Verificación de cierre — apartado 2.2

| Requisito del enunciado | Evidencia | Verificación |
|---|---|---|
| Máximos anuales desde resolución hasta 24 h | `ams_hydrological_oct_sep.csv` | 7 duraciones: 10 min, 30 min, 1 h, 3 h, 6 h, 12 h y 24 h. |
| Tres distribuciones | `quantiles_3methods.csv` | Gumbel, GEV y Log-Pearson III. |
| Tres métodos de ajuste | `quantiles_3methods.csv` | Momentos, L-momentos y máxima verosimilitud. |
| T = 2, 5, 10, 25, 50 y 100 años | `quantiles_3methods.csv` | 378 filas = 7 × 3 × 3 × 6; cada combinación tiene 6 cuantiles. |
| Pruebas de bondad de ajuste | `fit_summary_3methods.csv`, `seleccion_modelo_2_2.csv` | KS y Cramér–von Mises. |
| Diagrama de razones de L-momentos | `diagrama_lmomentos_2_2.png`, `lmoment_ratios_sample.csv` | Incorporado al anexo visible del informe PDF. |
| Bootstrap al 95 % | `bootstrap_ci_gev.csv` | Límites P2.5, mediana, P97.5 y ancho relativo. |
| Estacionariedad | `stationarity_hydrological_year.csv` | Tendencia revisada con el criterio de la Tarea 1. |

## Decisión

Se adopta GEV-MLE como referencia porque presenta el mejor compromiso entre KS,
Cramér–von Mises, flexibilidad de cola y estabilidad interpretada con bootstrap.
Los retornos altos, especialmente en 12–24 horas, se reportan con intervalos y
no como valores deterministas.
