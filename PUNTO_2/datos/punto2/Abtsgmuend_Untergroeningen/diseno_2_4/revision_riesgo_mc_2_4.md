# Riesgo Monte Carlo corregido (2.4A)

- Semilla: `20261123`; iteraciones: **5000**; réplicas bootstrap GEV válidas: **200**.
- Periodo de retorno nominal: **T = 25 años**, por lo que 1/T = **0.0400**.
- Probabilidad anual efectiva (promedio de CDF GEV por réplica): **0.009482**.
- Riesgo acumulado en 30 años: **0.248601 (24.860 %)**.
- Fracción diagnóstica de cargas que superan la capacidad en los sorteos: **0.0956**.

La fracción de indicadores no sustituye la probabilidad anual efectiva: el diseño
usa la probabilidad de excedencia de cada réplica GEV y luego la promedia. Por eso
una muestra finita puede tener cero excedencias directas sin implicar riesgo físico
nulo. Los parámetros muestreados y las probabilidades por iteración quedan en
`monte_carlo_A.csv`; la síntesis queda en `riesgo_A.csv`.
