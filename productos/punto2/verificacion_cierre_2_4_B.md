# Verificación del cierre de 2.4 B

Fecha de verificación: 24 de noviembre de 2026.

**Estado: NO CERRADO.** Se conservaron los resultados existentes y no se añadió lógica científica ni se modificaron parámetros. Los elementos 1, 5 y 6 del enunciado no están respaldados por archivos o cifras en la rama definitiva.

| Elemento exigido | Estado | Archivo y evidencia |
|---|---|---|
| 1. Hidrogramas trapezoidales del racional modificado para varias duraciones `d >= tc` | Faltante | No hay script, tabla ni figura trapezoidal en `codigo/punto2/`, `datos/punto2/` o `productos/punto2/`. |
| 2. Bloques alternos, varias duraciones y pico al inicio/centro/final | Completo | `datos/punto2/Abtsgmuend_Untergroeningen/diseno_2_4/tanque_escenarios.csv`: 30, 60 y 90 min, todas mayores que `tc = 4,2261 min` (`tc_comparacion.csv`), con las tres posiciones. El máximo de entrada en cada tránsito es 1,42749 m³/s. |
| 3. Piscina nivelada, `S(h)` y salida | Completo | `geometria_tanque.csv` y `codigo/punto2/finalizar_2_4.py`: `S(h)=528 h` m³; orificio de 0,30 m, `Cd=0,65`; salida a `h=2,0 m`: 0,28781 m³/s. |
| 4. Duración crítica, volumen y salida | Completo dentro de los escenarios de bloques | Escenario crítico: 60 min, pico final, 1019,28755 m³ y 1,93047 m. Tanque 24 x 22 m, profundidad útil 2,0 m, volumen 1056 m³; orificio 0,30 m. |
| 5. Comparación trapezoidal frente a bloques | Faltante | No existe volumen trapezoidal; por ello no puede hacerse la comparación exigida. |
| 6. `Qsal,max <= Qpico,preurbanización` con el mismo T | Faltante | El máximo de salida calculado entre los nueve escenarios es 0,28277 m³/s, pero no existe un `Qpico` preurbanización documentado con el mismo periodo de retorno. |

## Coherencia y efecto de la posición del pico

El volumen aumenta cuando el bloque más intenso se desplaza hacia el final porque llega después de que el almacenamiento ya ha crecido y queda menos tiempo para descargar por el orificio antes del máximo. En 30 min cambia de 885,12 m³ (inicio) a 1012,18 m³ (final); en 60 min, de 926,56 a 1019,29 m³; y en 90 min, de 908,83 a 964,52 m³.

El margen del escenario crítico es `1056,00 - 1019,29 = 36,71 m³`, equivalente a 3,60 % del volumen requerido (3,48 % de la capacidad). El margen sobrevive a los nueve escenarios de bloques calculados y la profundidad máxima de 1,93047 m no supera 2,0 m. No obstante, el margen no puede considerarse validado frente al hidrograma trapezoidal ausente ni frente al límite preurbanización aún no cuantificado.
