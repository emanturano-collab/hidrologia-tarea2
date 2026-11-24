# Matriz de análisis y calificación del Punto 2

## Alcance de la revisión

Esta matriz compara los requisitos disponibles del trabajo con la evidencia
actual del repositorio. El PDF original del enunciado no está disponible en el
entorno, por lo que la calificación es **provisional** y no sustituye la
rúbrica oficial. Los porcentajes usados en la matriz corresponden a los
criterios registrados en las auditorías previas del proyecto.

## Escala utilizada

| Nota | Significado |
|---:|---|
| 1 | No desarrollado o sin evidencia verificable |
| 2 | Desarrollo inicial, incompleto y con riesgos importantes |
| 3 | Desarrollo parcial; permite demostrar el método, pero faltan cierres |
| 4 | Desarrollo sólido, reproducible y casi completo; quedan limitaciones explícitas |
| 5 | Cumplimiento completo, consistente y verificable contra la rúbrica |

## Matriz por apartado

| Requisito | Qué solicita el trabajo | Evidencia actual | Estado | Nota 1–5 | Pendiente para nota 5 |
|---|---|---|---|---:|---|
| 2.0 Conceptos y ecuaciones | Definir variables, periodo de retorno, extremos, IDF, racional, Manning, tanque e incertidumbre | `2_0_conceptos_y_ecuaciones.md`; informe LaTeX | Alto | 4 | Integrar todas las fuentes metodológicas con citas autor-fecha y vincular cada ecuación a su salida |
| 2.1 Datos subdiarios y control de calidad | Serie ≤6 h, metadatos, coordenadas, faltantes, códigos, completitud y año hidrológico | DWD 00020; auditorías de calidad, intervalos, climatología y años hidrológicos | Alto | 4 | Adjuntar las fuentes brutas o una prueba limpia de reconstrucción desde cero |
| 2.2 Extremos y distribuciones | AMS, varias distribuciones y métodos, pruebas de ajuste, bootstrap, tendencia e interpretación | Gumbel, GEV, Log-Pearson III, KS, Cramér–von Mises, bootstrap, figuras y cuantiles | Alto | 4 | Explicar con mayor detalle la inestabilidad de retornos altos y la selección final |
| 2.3 Curvas IDF y fenómenos de lluvia | Curvas por duración y retorno, comparación externa, evento/anomalía e interpretación física | IDF GEV-MLE, KOSTRA, evento 2021, comparación CSV y gráfica | Alto | 4 | Añadir citas verificables para KOSTRA y desarrollar más la discusión de anomalías |
| 2.4A Alcantarilla/colector | Outlet, cuenca, C/CN, tc, caudal, diámetro, capacidad, incertidumbre y recomendación | DEM, outlet, WorldCover resumido, C=0.33421, Q=3.57173 m³/s, D=1.50 m, Manning y sensibilidad | Parcial alto | 3 | Versionar el raster WorldCover original y justificar completamente C, suelo y humedad antecedente |
| 2.4B Tanque de detención | Hietogramas, tránsito, salida, duración crítica, volumen, profundidad, borde libre y sensibilidad | Escenarios 30/60/90 min, posiciones del pico, tanque 24×22 m, 1056 m³, CSV de geometría | Alto | 4 | Añadir una figura esquemática y documentar con mayor detalle la ley de salida y sus supuestos |
| 2.5 Bonificación POT | Umbral, declustering, GPD, niveles de retorno y sensibilidad | P90/P95/P98, 24 h, CSV de niveles y comparación POT–GEV | Alto | 4 | Completar referencias bibliográficas y explicar la incertidumbre del ajuste GPD |

## Matriz por criterios generales de la rúbrica disponible

| Criterio | Peso registrado en auditorías previas | Evidencia | Nota 1–5 | Justificación |
|---|---:|---|---:|---|
| Diseño e incertidumbre | 24 % | Riesgo, sensibilidad de C/Manning/pendiente, Monte Carlo, tanque y alcantarilla | 3 | El diseño está calculado, pero el outlet es sintético, el riesgo empírico fue 0/5000 y falta el raster WorldCover original |
| Calidad de datos y metodología | 20 % | Serie DWD, metadatos, calidad, intervalos, año hidrológico y ventanas | 4 | La trazabilidad de lluvia es sólida; la corrección Weiss y la fuente de cobertura requieren documentación adicional |
| Resultados y cálculos | 12 % | CSV de AMS, ajustes, IDF, KOSTRA, geometrías y POT | 4 | Los resultados principales están disponibles y auditados; aún debe verificarse una ejecución limpia completa |
| Reproducibilidad y entrega | 12 % | Scripts, README, auditoría 10/10 y archivos derivados | 4 | La estructura es reproducible, pero el raster de cobertura no está incluido y el PDF LaTeX no se pudo recompilar en este entorno |
| Comunicación y transparencia de IA | 6 % | Declaración de uso de IA y PDF narrativo | 4 | La declaración existe; faltan citas autor-fecha sistemáticas y una comprobación APA 7 completa |

### Promedio provisional de los criterios ponderados disponibles

Con los pesos que sí aparecen documentados en el proyecto, la valoración
provisional es aproximadamente **3.6/5**. No es una nota oficial porque el PDF
de la rúbrica no está disponible para confirmar si existen criterios
adicionales o una ponderación distinta.

## Auditoría de citas y referencias

| Fuente o afirmación | ¿Está citada? | ¿Es verificable? | Acción |
|---|---|---|---|
| DWD estación 00020 y serie RWS_10 | Parcial | Sí, por archivos y metadatos locales | Añadir referencia bibliográfica completa del producto DWD |
| SRTM DEM | Sí en referencias | Parcial | Añadir versión, resolución, fecha y enlace de descarga |
| ESA WorldCover 2021 | Sí en referencias | Parcial | Adjuntar el raster original o su URL/versionado; actualmente solo queda la tabla reconstruida |
| KOSTRA-DWD-2020 | Mencionada | Parcial | Añadir referencia oficial completa y enlace a la versión utilizada |
| OpenStreetMap | Sí en LaTeX | Sí | Mantener fecha de consulta y URL |
| Chow et al. (1988) | Mencionada | Sí | Completar formato APA 7 y usar cita autor-fecha en el cuerpo |
| Métodos estadísticos y Weiss | Insuficiente | Parcial | Incorporar las referencias metodológicas recomendadas por el enunciado |
| Uso de IA | Sí | Sí como declaración | Especificar herramientas, tareas y verificaciones humanas sin atribuir resultados a la IA |

## Dictamen

El Punto 2 está **bien desarrollado y técnicamente avanzado**, con evidencia
para todos los apartados 2.0–2.5. Sin embargo, no puede calificarse como 5/5 ni
como 100 % cerrado mientras no se resuelvan tres aspectos: (1) disponer del
PDF oficial para verificar literalmente la rúbrica, (2) adjuntar/versionar el
raster WorldCover original y (3) completar las citas APA 7 y la comprobación de
compilación final del informe.
