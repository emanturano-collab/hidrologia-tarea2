# Guion para la presentación oral

## Secuencia sugerida (8–10 minutos)

1. **Problema y datos (1 min):** estación DWD 00020, resolución de 10 minutos,
   microcuenca sintética delimitada con SRTM y cobertura ESA WorldCover 2021.
2. **Control de calidad (1 min):** explicar completitud anual, códigos de
   calidad, año hidrológico y el criterio de Weiss para no ocultar años con
   cobertura insuficiente.
3. **Extremos e IDF (2 min):** justificar máximos anuales, GEV-MLE, bootstrap,
   comparación con KOSTRA-DWD-2020 y separación entre anomalía, evento extremo
   y tendencia.
4. **Diseño 2.4A (2 min):** mostrar coberturas, `C=0.33239`, `tc` de Kirpich
   `4.226 min`, `Qp=3.55778 m³/s` y la alcantarilla de `1.50 m`.
5. **Diseño 2.4B (1 min):** explicar la ley de salida, tránsito por pasos de
   10 min, volumen requerido `1014.75 m³` y tanque útil `1056 m³`.
6. **Sensibilidad y cierre (1–2 min):** mencionar variaciones de `C`, Manning,
   pendiente y `tc`; terminar con las limitaciones del outlet sintético y el
   riesgo residual de `24.86 %` en 30 años.

## Preguntas previsibles y respuestas

- **¿Por qué GEV-MLE?** Es la distribución principal para máximos anuales; se
  contrastó con bootstrap y POT, sin ocultar la incertidumbre de la cola.
- **¿Por qué la estación es representativa?** La estación aporta la señal
  pluviométrica subdiaria; la microcuenca se delimitó espacialmente por DEM y
  el outlet es sintético, por lo que no se afirma que exista un aforo allí.
- **¿Cómo se eligió `C`?** Se ponderaron coberturas originales WorldCover con
  coeficientes explícitos y se reportó sensibilidad ±20 %.
- **¿El diseño garantiza ausencia de inundación?** No. Es un diseño preliminar;
  la capacidad supera `Qp`, pero el riesgo residual exige medidas de seguridad
  y verificación hidráulica detallada.
- **¿Qué limita la conclusión?** Serie puntual, extrapolación de retornos,
  incertidumbre espacial, supuestos de suelo/Manning y outlet sintético.
- **¿Qué hizo la IA?** Apoyó automatización, gráficos y revisión; el grupo
  verificó datos, corrigió inconsistencias y conserva la responsabilidad
  metodológica y académica.
