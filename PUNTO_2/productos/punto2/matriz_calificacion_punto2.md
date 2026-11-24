# Matriz de análisis y calificación — Punto 2

## 1. Base de la revisión

La fuente normativa utilizada es `anexos/tarea2_enunciado.pdf`, páginas 18–21 (requisitos 2.1–2.5), y página 4 (rúbrica del trabajo escrito). El enunciado establece que los puntos 1 y 2 son independientes, por lo que esta matriz evalúa el avance del punto 2 sin atribuirle resultados de evapotranspiración del punto 1.

La escala del profesor es de 0 a 5: **Excelente** 4.5–5.0, **Sólido** 3.5–4.4, **Básico** 3.0–3.4, **Insuficiente** 0.1–2.9 y **Sin evidencia** 0. La nota ponderada se calcula como \(N=\sum (w_i/100)n_i\). Las bonificaciones de 2.5 son adicionales y solo aplican si el trabajo escrito obligatorio alcanza 3.0.

## 2. Verificación de requisitos del punto 2

| Apartado del enunciado | Evidencia localizada | Estado actual | Nota de avance (1–5) | Qué falta para 5.0 |
|---|---|---|---:|---|
| **2.0 Riesgo y diseño** | `2_0_conceptos_y_ecuaciones.md`, `cierre_final_punto2.md`, escenarios y discusión de riesgo | Cumplido con reservas | 4.0 | Integrar en el informe una justificación explícita de vida útil, consecuencias de falla, riesgo aceptable y práctica de Chow; corregir la cifra de riesgo inconsistente entre el informe y el cierre final. |
| **2.1 Serie subdiaria y control de calidad** | DWD 00020, 10 min (2005–2025), metadatos, coordenadas, auditorías de intervalos, códigos, faltantes y años hidrológicos | Sólido alto | 4.6 | Incorporar la tabla/resumen de completitud directamente en el informe y repetir una ejecución limpia desde cero antes del ZIP. |
| **2.2 Extremos y ajustes** | AMS 10 min–24 h; Gumbel, GEV y Log-Pearson III; métodos y pruebas KS/CvM; bootstrap; tendencia | Sólido | 4.0 | Incorporar en el informe la tabla completa para T = 2, 5, 10, 25, 50 y 100 años por distribución y método, diagrama de razones de L-momentos y la justificación física/estadística de GEV-MLE. |
| **2.3 IDF y evento/anomalía** | IDF GEV-MLE, bandas, comparación KOSTRA-DWD-2020, evento 2021 y retorno estimado | Sólido con reservas | 3.8 | Añadir parámetros y error de la expresión analítica, rango válido, evento intenso con intervalo de incertidumbre, fuente oficial verificable de KOSTRA y una discusión física de anomalía que no confunda evento aislado con tendencia. |
| **2.4A Alcantarilla/colector** | DEM, microcuenca 0.123154 km², cauce, cobertura ponderada, C=0.33239, tres tc, Qp, Manning, diámetro 1.50 m, sensibilidad, Monte Carlo y escala | Sólido alto | 4.4 | Integrar suelo/humedad antecedente y la limitación del outlet sintético en la recomendación final; la escala, sensibilidad y WorldCover ya están documentadas. |
| **2.4B Tanque** | Hietogramas de bloques alternos con tres posiciones, hidrogramas, tránsito, duración crítica, 1014.75 m³ requeridos, tanque 24×22 m y 1056 m³ útiles | Sólido alto | 4.4 | Integrar la ley de salida, el esquema y la comparación de escenarios en el cuerpo principal del informe; ya están disponibles en anexos y PDF. |
| **2.5 Bonificaciones** | POT P90/P95/P98, declustering 24 h, GPD, niveles de retorno y comparación POT–GEV | Evidencia de análisis; bono condicionado | 3.6 | Para obtener bonos, incluir referencias y justificación del umbral/independencia, incertidumbre GPD y el análisis específico de cada ítem 2.5.1–2.5.5. Actualmente no hay evidencia completa de mínimo costo, no estacionariedad, confiabilidad/resiliencia/vulnerabilidad ni cópula. |

## 3. Calificación de la rúbrica del trabajo escrito

| Criterio oficial (página 4) | Peso | Evidencia y juicio | Nota 1–5 | Estado |
|---|---:|---|---:|---|
| Interpretación física (punto 1) | 26 % | El informe conserva un espacio reservado, pero no contiene el análisis de evapotranspiración, Budyko, atribución ni proceso propio de la cuenca. Este criterio no puede considerarse entregado en la revisión del punto 2. | **0.0** | Pendiente del equipo del punto 1 |
| Criterio de diseño e incertidumbre (punto 2) | 24 % | Hay diseño completo de A y B, sensibilidad, Monte Carlo y recomendación. El raster WorldCover ya está incorporado y el riesgo quedó unificado; todavía falta completar escala, suelo/humedad y cierre documental. | **4.1** | Sólido |
| Calidad de datos y metodología | 20 % | Serie DWD y auditorías sólidas; ahora hay raster WorldCover original, metadatos, SHA-256, completitud anual (20 años válidos) y decisión documentada de Weiss. Falta integrar estas evidencias en el PDF final. | **4.4** | Sólido alto |
| Resultados y cálculos | 12 % | CSV, figuras, IDF, KOSTRA, Qp, Manning, tanque y POT auditados (10/10 controles internos). La discrepancia de riesgo y el reporte incompleto de tablas exigidas impiden 4.5–5.0. | **3.5** | Sólido bajo |
| Reproducibilidad y entrega | 12 % | Código, datos y README existen, pero todavía no se ha generado/verificado el ZIP con el nombre y la estructura exactos exigidos; falta el raster WorldCover y una prueba limpia completa. | **3.0** | Básico |
| Comunicación y transparencia de IA | 6 % | Hay informe, referencias y declaración general de IA. La declaración aún no enumera de forma completa versión de herramientas, tareas, resultados verificados, propuestas rechazadas y contribución individual; las citas autor–fecha son incompletas. | **3.2** | Básico alto |

### Nota calculable con la evidencia actual

- **Avance normalizado del punto 2 (sin el criterio de punto 1):** 3.44/5 sobre el 74 % evaluable (criterios de diseño, datos, resultados, reproducibilidad y transparencia).
- **Nota del trabajo escrito completo si se cerrara hoy y el punto 1 siguiera vacío:** 2.55/5, porque el criterio de interpretación física vale 26 %. Esta no es una predicción de la nota final: cambiará al incorporar y verificar el punto 1.
- **Bonos:** no se suman todavía. El POT documentado puede sustentar el bono de excedencias solo después de cumplir el rigor y la trazabilidad exigidos; los bonos 2.5.1–2.5.5 requieren evidencia adicional específica.

## 4. Auditoría de referencias y citas

| Fuente/afirmación | Verificabilidad actual | Acción requerida |
|---|---|---|
| DWD 00020 y serie de 10 minutos | Archivos brutos y metadatos locales; verificable | Añadir referencia DWD completa, URL, versión y fecha de descarga en APA 7. |
| SRTM DEM | Archivo local y referencia general | Especificar producto, resolución, versión, URL y fecha de descarga. |
| ESA WorldCover 2021 | Tabla reconstruida; raster original ausente | Incluir el raster usado o un procedimiento reproducible de descarga y checksum. |
| KOSTRA-DWD-2020 | Archivos ASC y comparación local | Citar publicación/portal oficial, versión, celda y fecha de consulta. |
| OSM, Chow, Kirpich, Manning y métodos estadísticos | Parcialmente listados | Usar citas autor–fecha en el texto y completar referencias APA 7. |
| POT, GEV, bootstrap y Weiss | Código y productos disponibles | Vincular cada método a una fuente metodológica y reportar decisiones, no solo resultados. |
| Uso de IA | Declaración general presente | Añadir las cinco partes solicitadas por el enunciado y responsabilidades individuales. |

## 5. Dictamen

El punto 2 tiene una base técnica sólida y evidencia para 2.1–2.5, pero **no alcanza aún 5/5 ni puede declararse entrega final**. Las tres correcciones prioritarias son: (1) resolver la discrepancia del riesgo efectivo y dejar una cifra única trazable; (2) incorporar el raster/metadata reproducible de WorldCover y completar las justificaciones de cobertura, escala y outlet; y (3) preparar el ZIP con nombre/estructura exactos, tablas exigidas, citas APA 7 completas y declaración de IA detallada. El PDF oficial queda conservado en `anexos` como fuente normativa de esta revisión.
