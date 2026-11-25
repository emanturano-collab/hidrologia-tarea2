# Registro de la revisión final (24 de noviembre de 2026)

Revisión hecha con Claude Opus 5.5 (Anthropic, mediante Claude Code) a pedido del interventor del trabajo, sobre la rama `ENTREGA-PREFINAL`. El trabajo se hizo en la rama local `entrega-final`. Este registro forma parte de la declaración de uso de IA del informe.

## 1. Organización

| Cambio | Motivo |
|---|---|
| Se trajeron de `main` el raster ESA WorldCover 2021 (SHA-256 verificado), sus metadatos, la completitud anual, la escala del método racional, las métricas IDF, los scripts asociados y el enunciado (`anexos/enunciado/`). | `ENTREGA-PREFINAL` había excluido el material exclusivo de `main`; sin el raster no se podía regenerar C. |
| Se eliminaron copias duplicadas en `codigo/punto1/` y la versión antigua de `run_1_4.py`, que no calculaba la atribución. | Duplicados con contenido distinto inducían a error. |
| La solicitud de humedad del suelo marcada como "PENDIENTE" se renombró como histórica y se corrigió su texto en el script que la genera. | Contradecía los metadatos: la humedad sí se descargó y procesó. |
| Los informes de avance del punto 2 (`productos/punto2/*.md`) se movieron a `anexos/historial_versiones/punto2_borradores/`. | Tenían cifras de versiones anteriores (riesgo de 21,9 %, 24,86 % y 25,06 %; tanque de 1014,75 y 1019,29 m³) que contradicen las definitivas. |
| El README anterior se movió a `anexos/historial_versiones/README_entrega_prefinal.md` y se escribió uno nuevo. | El enunciado exige integrantes, carpetas, procedencia, requisitos y orden de ejecución. |
| `codigo/requirements.txt` se reescribió con las versiones reales. | Listaba módulos locales como si fueran paquetes y no tenía versiones. |
| Se creó `codigo/crear_zip_entrega.py`. | Arma el ZIP con el nombre y la estructura exigidos y los valida. |

## 2. Correcciones de método en el punto 2

| Problema encontrado | Corrección | Efecto |
|---|---|---|
| La fórmula del retardo del SCS tenía intercambiadas la pendiente y la retención potencial `1000/CN − 10`. | Se usó la forma del NRCS (2010), con L en pies, retención en pulgadas y pendiente en %. | tc SCS pasó de 9,4 a 12,5 min. |
| No se aplicó la corrección de Weiss con el argumento de usar ventanas móviles. | Una ventana móvil de n intervalos fijos de reloj es justamente el caso de Weiss (1964); se aplicó `1/(1 − 1/(8n))`. | +14,3 % en 10 min, +2,1 % en 1 h. |
| `extremos_2_2/lmoment_ratios_sample.csv` tenía τ3 ≈ 0,04–0,09; el valor real es 0,25–0,51. | Se recalcularon los L-momentos y se rehízo el diagrama. | La muestra tiene cola más pesada que Gumbel. |
| La GEV-MLE con N = 20 producía réplicas bootstrap degeneradas (cuantiles de 10¹³ mm/h). | Se adoptó la GEV-GMLE de Martins y Stedinger (2000) como distribución de diseño; la GEV-MLE queda como sensibilidad. | Bandas IDF razonables; local/KOSTRA a 1 h y T = 100 pasa de 2,08 a 1,52. |
| El evento del 24/07/2013 (81 mm en 1 h) no se había analizado. | Control de calidad del evento y sensibilidad excluyéndolo. | Explica la diferencia con KOSTRA. |
| El diámetro de 1,50 m no salía de redondear al comercial superior (el calculado era 1,16 m). | Se aplicó la regla del enunciado y se añadió el criterio de riesgo efectivo. | Recomendación: 1,05 m (T efectivo ≈ 95 años). |
| El tanque (2.4 B) descargaba como máximo 0,28 m³/s, sin relación con el pico previo a la urbanización (3,56 m³/s), y no tenía escenario urbanizado. | Escenario urbanizado (C = 0,60, CN = 90), orificio dimensionado para Q_pre, hidrogramas trapezoidales, bloques alternos con tiempo-área y comparación de volúmenes. | 2.4 B completo. |
| Las cifras del informe se escribían a mano y no coincidían entre secciones. | Todas las cifras salen de `cifras_punto1.tex` y `cifras_punto2.tex`, que generan los scripts. | Una sola fuente de verdad. |

## 3. Informe y presentación

- El informe nuevo (`anexos/informe_fuente/informe.tex`) sigue las cinco secciones del enunciado, integra el punto 1 a partir de los productos existentes y aplica APA 7: citas autor-año, 33 referencias con DOI cuando existe, y tablas y figuras numeradas con título.
- La presentación (`anexos/informe_fuente/presentacion.tex`) tiene 10 diapositivas de 16:9 que cubren los dos puntos.
- El informe anterior (solo punto 2) quedó en `anexos/historial_versiones/informe_tarea2_main_v0.tex`.

## 4. Decisiones que el grupo debe aprobar

Están en `codigo/punto2/config_diseno_2_4.json` (claves `REVISAR_GRUPO`) y en rojo en el informe:

1. Distribución de diseño GEV-GMLE.
2. tc del SCS (CN = 75) como valor de diseño.
3. T = 25 años, vida útil de 30 años y riesgo aceptable de 75 %.
4. Criterio del riesgo efectivo para el diámetro (1,05 m).
5. C urbanizado = 0,60 y CN = 90 para el tanque.
6. La rama del árbol de decisión de las notas del curso citada en 1.1.d.
7. Las hipótesis sobre los trasvases Chotano–Conchano en 1.2 y 1.3.

## 5. Verificación de reproducibilidad del punto 1

Se ejecutaron desde cero 15 scripts del punto 1 que en la verificación prefinal solo estaban compilados (1.1.c, 1.1.d, 1.2.2, 1.2.3, 1.2.4, 1.3, 1.4 y 1.5). Todas sus tablas coinciden con las versiones guardadas, con diferencias relativas menores de 10⁻⁷. Solo cambiaron los inventarios y registros de fuentes, que antes guardaban rutas con el prefijo `tarea 02\` y ahora usan rutas relativas.

- `run_1_1c_metodos_alternativos.py` necesitaba `tabulate`, que no estaba en `requirements.txt`; se agregó.
- `run_1_1b_station_vs_era5_chiclayo.py` falla porque el ZIP de ERA5-Land de Chiclayo no está en el repositorio (ver README).
