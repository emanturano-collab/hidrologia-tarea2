# Cierre final técnico del Punto 2

## Estado general

El punto 2 queda cerrado técnicamente para los apartados 2.0–2.5 con la
salvedad de que el raster ESA WorldCover original no está incluido en esta
copia. La tabla de cobertura y el coeficiente ponderado se conservaron como
evidencia reconstruida y están marcados con esa limitación.

## Resultados finales verificables

- Estación: DWD 00020, Abtsgmünd–Untergröningen, 48.9219 N, 9.9129 E.
- Serie: 10 minutos, 2005–2025; años hidrológicos completos 2006–2025.
- Microcuenca: 0.123154 km²; cauce principal 382.69 m; pendiente 0.12543 m/m.
- 2.2: comparación Gumbel, GEV y Log-Pearson III; referencia GEV-MLE con
  bootstrap y pruebas KS/Cramér–von Mises.
- 2.3: IDF GEV-MLE y comparación con KOSTRA-DWD-2020; archivos de comparación
  y gráfica incluidos.
- 2.4A: C=0.33421, tc de Kirpich=9.436 min, Qp=3.57173 m³/s, alcantarilla
  de 1.50 m y capacidad 7.076 m³/s.
- 2.4B: tanque de 24 × 22 m, 1056 m³ útiles, requerimiento 1019.29 m³,
  profundidad máxima 1.93 m y margen 36.71 m³.
- 2.5: POT con umbrales P90, P95 y P98, declustering de 24 h y comparación
  reproducible contra GEV-MLE.

La auditoría automática reporta 10/10 comprobaciones internas correctas. El
Monte Carlo corregido usa 5000 iteraciones y 200 réplicas bootstrap GEV, con
semilla 20261123. La probabilidad anual efectiva es 0.009569 y el riesgo
acumulado en 30 años es 0.250570 (25.057 %). La fracción diagnóstica de cargas
que superan directamente la capacidad es 0.0978; no sustituye la probabilidad
integrada de excedencia de la CDF GEV.

## Pendientes de entrega

1. Adjuntar o versionar el raster WorldCover 2021 original.
2. Compilar y revisar visualmente el PDF final con figuras, referencias APA 7
   y la sección reservada para el Punto 1.
3. Mantener la limitación del outlet sintético en resultados y conclusiones.
