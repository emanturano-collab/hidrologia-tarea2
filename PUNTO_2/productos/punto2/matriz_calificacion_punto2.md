# Matriz de calificación actualizada — Punto 2

**Fecha de revisión:** 24 de noviembre de 2026  
**Fuente normativa:** `anexos/tarea2_enunciado.pdf`, requisitos 2.0–2.5 y rúbrica del trabajo escrito.

## 1. Cumplimiento técnico del punto 2

| Apartado | Evidencia actual | Nota (0–5) | Reserva para 5.0 |
|---|---|---:|---|
| **2.0 Conceptos que usarán** | Riesgo, periodo de retorno, AMS/POT, GEV, métodos, Weiss, IDF, FRA, tc, racional, Manning y tránsito explicados. | **4.2** | Falta vincular explícitamente periodo de retorno, consecuencias de falla y práctica de Chow en una tabla de decisión. |
| **2.1 Datos subdiarios y control de calidad** | DWD 00020 a 10 min, metadatos, coordenadas, códigos, faltantes, años hidrológicos, Weiss, completitud y DEM. | **4.2** | El informe resume el control, pero no muestra todos los criterios de años válidos y sensibilidad de descarte. |
| **2.2 Extremos y ajuste** | AMS 10 min–24 h; Gumbel, GEV y Log-Pearson III; tres métodos; KS/CvM; cuantiles, bootstrap y L-momentos integrados en 2.2. | **4.5** | La tabla visible está desarrollada para 10 min; para 5.0 convendría mostrar una tabla compacta equivalente por todas las duraciones. |
| **2.3 Curvas IDF** | Curvas, parámetros, errores, rango válido, KOSTRA con DOI, evento 2021 e intervalo, y separación anomalía–evento–tendencia. | **4.4** | Hacer más visible en la figura principal la incertidumbre para dos retornos y ampliar la interpretación areal. |
| **2.4A Problema A** | DEM, microcuenca, cauce, pendiente, WorldCover, C=0.33239, tres tc, Qp, Manning, D=1.50 m, escala, sensibilidad y Monte Carlo. | **4.3** | Ampliar suelo/humedad antecedente, riesgo aceptable y práctica de diseño; el outlet sigue siendo sintético. |
| **2.4B Problema B** | Hietogramas, posiciones del pico, tránsito, ley de salida, volumen, tanque, esquema y sensibilidad integrados en 2.4B. | **4.3** | Añadir tabla comparativa explícita entre hidrogramas trapezoidales y hietograma, y tamaño de salida. |
| **2.5 Bonificaciones** | POT P90/P95/P98 y comparación POT–GEV como análisis complementario. | **3.5** | POT no equivale automáticamente a bonos 2.5.1–2.5.5; faltan evidencias específicas de esos ítems. |

## 2. Rúbrica del trabajo escrito

| Criterio oficial | Peso | Nota | Juicio |
|---|---:|---:|---|
| Interpretación física (punto 1) | 26 % | **0.0** | El punto 1 sigue reservado; faltan evapotranspiración, Budyko, atribución y proceso de cuenca. |
| Diseño e incertidumbre (punto 2) | 24 % | **4.3** | Diseño A/B, sensibilidad, riesgo efectivo, recomendación y escala presentes. |
| Calidad de datos y metodología | 20 % | **4.3** | Serie subdiaria, QA/QC, WorldCover, metadatos, checksum, métodos y unidades trazables. |
| Resultados y cálculos | 12 % | **4.2** | Resultados, tablas y figuras verificables; puede mejorar incertidumbre y comparación de 2.4B. |
| Reproducibilidad y entrega | 12 % | **4.3** | ZIP validado, rutas relativas y auditoría limpia 10/10; aún provisional por `G00` y punto 1 reservado. |
| Comunicación y transparencia de IA | 6 % | **4.4** | Estructura 2.0–2.5, APA 7, declaración de IA y guion oral. |

### Nota estimada del trabajo escrito completo

\[
N = 0.26(0.0)+0.24(4.3)+0.20(4.3)+0.12(4.2)+0.12(4.3)+0.06(4.4)
\]

**Nota estimada actual: 3.18 / 5.0**, sin bonos y suponiendo que el punto 1 se entrega vacío.

### Nota estimada del componente punto 2

Excluyendo temporalmente el criterio del punto 1, el componente técnico del punto 2 queda aproximadamente en **4.3 / 5.0**, nivel **sólido alto**.

### Bonificaciones

No se suman automáticamente. POT es una sensibilidad útil, pero los bonos del enunciado requieren demostrar los ítems 2.5.1–2.5.5. El tope es +0.5 y solo aplica si la nota obligatoria es ≥3.0.

## 3. Prioridades para subir la nota

1. Integrar completamente el punto 1: interpretación física, Budyko, atribución y proceso de la cuenca.
2. Añadir tabla de periodo de retorno con vida útil, riesgo aceptable, consecuencias y práctica de Chow.
3. Mostrar bandas IDF y comparación cuantitativa trapezoidal–hietograma para 2.4B.
4. Sustituir `G00` por el número oficial e incorporar el punto 1 al ZIP final.
5. Desarrollar cada bono 2.5.1–2.5.5 con cálculo, incertidumbre y referencia verificable.

## 4. Actualización después de la Fase 2 — 24 de noviembre de 2026

| Bono | Evidencia nueva | Dictamen de calificación |
|---|---|---|
| **2.5.1** | Curva de costo esperado para T=2–100 años usando máximos de 10 min escalados a `tc`, FRC y sensibilidad `Dmax/2`, `Dmax`, `2Dmax` y tasas 3/6/9 %. | **+0.2 técnicamente sustentable**, pendiente solo de revisión de supuestos económicos por el grupo. |
| **2.5.2** | POT P95, declustering 24 h, ajuste GPD y comparación con AMS mediante Langbein. | **0.05 provisional**; puede subir a +0.1 tras verificar la equivalencia de periodos y la incertidumbre GPD. |
| **2.5.3** | Escenario 7 %/°C con diámetros equivalentes de 1.50–1.62 m y periodo efectivo de 25.0 a 14.8 años para 0–3 °C. | **0.0 provisional** hasta contrastar el escenario con temperatura observada y justificar la elección climática. |
| **2.5.4** | Serie horaria completa convertida a caudal; 0 horas exceden la capacidad de 7.076 m³/s. | **0.0 provisional**: un resultado nulo no demuestra por sí solo confiabilidad, resiliencia y vulnerabilidad; falta validar racional tiempo–área y periodo de desempeño. |
| **2.5.5** | Cópula gaussiana exploratoria entre intensidad y duración. Los umbrales conjuntos no registran excedencias en 21 años. | **0.0 provisional** hasta ajustar márgenes continuos, seleccionar cópula formal y estimar incertidumbre. |

**Bonificación técnicamente sustentable hoy:** `+0.2` por 2.5.1, con `+0.1` potencial por 2.5.2 después de revisión. Los bonos 2.5.3–2.5.5 siguen exploratorios. La nota obligatoria del trabajo completo permanece `3.18/5.0` porque el punto 1 continúa incompleto; el componente técnico del punto 2 puede llegar a `5.0` al validar los cinco bonos.
