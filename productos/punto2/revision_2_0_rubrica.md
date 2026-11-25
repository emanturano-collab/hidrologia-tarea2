# Revisión de cumplimiento — apartado 2.0

## Dictamen

El documento `2_0_conceptos_y_ecuaciones.md` **cumple como base metodológica del
apartado 2.0**, pero no puede considerarse por sí solo el cumplimiento del 100 %
de la rúbrica del punto 2. La rúbrica evalúa resultados de extremos, IDF,
diseño, incertidumbre y reproducibilidad; esos elementos se completan en 2.1–2.4.

Estado de la fase 2.0: **80 % — borrador metodológico sólido, pendiente de
integración en el informe y verificación de consistencia durante los cálculos**.

## Matriz contra la rúbrica

| Criterio de la rúbrica | Evidencia existente en 2.0 | Estado | Corrección necesaria |
|---|---|---|---|
| Diseño e incertidumbre (24 %) | Define `T`, `p`, riesgo de vida útil, FRA, sensibilidad y Monte Carlo | Parcial | Los valores, orden de incertidumbres, riesgo efectivo y recomendación solo se obtienen en 2.2–2.4 |
| Calidad de datos y metodología (20 %) | Define ventanas, unidades, ecuaciones, signos y supuestos | Parcial alto | Integrar fuentes completas, año hidrológico, faltantes y decisiones reales de la serie |
| Resultados y cálculos (12 %) | No presenta cuantiles, IDF, Qp, diámetro ni volumen | Pendiente | Se completa con 2.2, 2.3 y 2.4 |
| Reproducibilidad y entrega (12 %) | Documento versionado dentro del repositorio | Parcial | Vincular cada ecuación al script, parámetros, entradas y salidas reproducibles |
| Comunicación y transparencia de IA (6 %) | El texto es claro y explicita supuestos | Parcial | Añadir referencias completas, declaración de IA y contribución de integrantes |

## Comprobaciones técnicas realizadas

- `T = 1/p` y `R_n = 1 - (1 - 1/T)^n` están correctamente diferenciados.
- La conversión racional `Qp = C i A / 3.6` usa `i` en mm/h y `A` en km².
- La ponderación `C = sum(Ck Ak) / A` es consistente.
- La ecuación de Manning y el redondeo al diámetro comercial están incluidos.
- El balance del tanque y la salida por orificio están incluidos.
- Se añadieron unidades y convención de signos para evitar errores de balance.
- Se incluyó la necesidad de citar Chow, Weiss, Svensson–Jones y Kuiry–Sen.

## Riesgos de perder puntos si no se corrigen en fases posteriores

1. Presentar una ecuación sin la fuente o sin explicar sus límites físicos.
2. Usar el año calendario sin justificar el año hidrológico.
3. Reportar un diámetro sin bandas de incertidumbre, sensibilidad y riesgo
   efectivo.
4. Confundir un periodo de retorno de `T` años con una ocurrencia periódica.
5. Mezclar mm, mm/h, m³/s, km² y m² sin conversiones explícitas.
6. No demostrar que el outlet de la microcuenca conduce a una vía, canal o zona
   urbana.

## Decisión de avance

La fase 2.0 queda aprobada como **base conceptual**. No se debe declarar
"punto 2 terminado" hasta cerrar 2.1–2.4. La siguiente revisión será 2.1:
definir año hidrológico, comprobar temporada de tormentas e integrar la
justificación espacial de la microcuenca.
