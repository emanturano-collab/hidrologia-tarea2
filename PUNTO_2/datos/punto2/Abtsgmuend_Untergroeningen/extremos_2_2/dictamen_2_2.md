# Dictamen final del apartado 2.2

## Cobertura del análisis

Se calcularon máximos anuales hidrológicos para 10 minutos, 30 minutos, 1, 3,
6, 12 y 24 horas. Para cada duración se ajustaron Gumbel, GEV y Log-Pearson
III por momentos, L-momentos y máxima verosimilitud. Se conservaron cuantiles
para T = 2, 5, 10, 25, 50 y 100 años en `quantiles_3methods.csv`.

## Selección de distribución y método

La decisión final es **GEV por máxima verosimilitud (GEV-MLE)**. Para la
duración de 10 minutos, su KS = 0.8567 y CvM = 0.8998 superan los valores de
Gumbel-MLE (0.6249 y 0.6594) y Log-Pearson III-MLE (0.8234 y 0.8612). GEV
además permite un parámetro de forma para representar colas que no tienen que
ser Gumbel. No se eligió solo por el menor estadístico: también se revisaron
gráficos de probabilidad, razones de L-momentos y estabilidad bootstrap.

## Incertidumbre

Los intervalos bootstrap GEV-MLE están en `bootstrap_ci_gev.csv` y se muestran
en el informe para la duración de 10 minutos. El ancho relativo aumenta hacia
T = 50–100 años y se vuelve particularmente grande en 12–24 horas. Por ello,
los cuantiles altos son extrapolaciones de la muestra de 20 años y deben
reportarse con intervalo, no como un valor determinista.

## Evidencias

- `quantiles_3methods.csv`: tabla completa de distribuciones, métodos, duraciones y T.
- `diagrama_lmomentos_2_2.png`: razones de L-momentos.
- `graficas_probabilidad_2_2.png`: comparación visual de ajustes.
- `bootstrap_ci_gev.csv`: intervalos y ancho relativo.
- `stationarity_hydrological_year.csv`: prueba de tendencia.
