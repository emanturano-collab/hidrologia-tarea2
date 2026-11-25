# Guía del punto 2 organizada por apartados del PDF

Esta guía sigue el orden exacto del enunciado: **2.0 conceptos, 2.1 datos,
2.2 extremos, 2.3 curvas IDF, 2.4 problemas de diseño, 2.5 bonificaciones y
Síntesis del punto 2**. El porcentaje indica el avance real del apartado, no una
calificación definitiva.

## Resumen de avance

| Apartado del PDF | Tema | Avance actual | Estado |
|---|---|---:|---|
| 2.0 | Conceptos y ecuaciones | 80 % | Documento preparado; falta integrarlo y revisarlo con el informe |
| 2.1 | Datos subdiarios y control de calidad | 100 % | Cerrado; la validación final del outlet se conserva para 2.4 |
| 2.2 | Extremos y distribuciones | 95 % | Gráficas, pruebas y bootstrap listos; falta la discusión final del grupo |
| 2.3 | Curvas IDF | 75 % | IDF, evento reciente y comparación KOSTRA listos; falta revisión final de incertidumbre |
| 2.4 A | Alcantarilla/colector, método racional | 80 % | Coberturas, C, geometría, capacidad y sensibilidad listos; falta validar outlet |
| 2.4 B | Tanque de detención | 70 % | Hietograma corregido, duración crítica y geometría preliminar listos; falta validar obra |
| 2.5 | Bonificaciones | 0 % | Opcional; no debe retrasar lo obligatorio |
| Síntesis | Recomendación, incertidumbre y conclusiones | 10 % | Estructura preparada; resultados pendientes |

La nota del escrito depende especialmente de diseño e incertidumbre (24 %),
calidad de datos y metodología (20 %), resultados (12 %), reproducibilidad
(12 %) y comunicación/transparencia de IA (6 %).

---

## 2.0. Conceptos que deben usarse con precisión

### Objetivo del apartado

Definir correctamente probabilidad de excedencia, periodo de retorno, riesgo de
vida útil, IDF, reducción areal, tiempo de concentración, método racional,
Manning y tránsito en tanque.

### Lo que ya está avanzado — 80 %

- La guía identifica las ecuaciones que se usarán.
- La microcuenca está dentro del rango donde el método racional es defendible.
- La estructura de riesgo nominal frente a riesgo efectivo ya está definida.
- Se creó `PUNTO_2/productos/punto2/2_0_conceptos_y_ecuaciones.md` con definiciones,
  ecuaciones, unidades y supuestos.

### Lo que falta para cerrarlo

1. Escribir las definiciones y unidades en la metodología.
2. Diferenciar siempre periodo de retorno `T`, probabilidad anual `p = 1/T` y
   riesgo durante una vida útil.
3. Definir profundidad, intensidad, duración, área, caudal, almacenamiento y
   descarga con sus unidades.
4. Explicar los supuestos físicos del método racional y de Manning.
5. Explicar por qué la lluvia puntual del pluviómetro puede representar la
   microcuenca y cuándo debe aplicarse un factor de reducción areal.

### Criterio de cierre

Un lector puede reconstruir las ecuaciones, unidades y supuestos sin buscar
definiciones externas.

---

## 2.1. Datos subdiarios y control de calidad

### Objetivo del apartado

Demostrar que la serie de Abtsgmünd es válida para construir máximas anuales e
IDF.

### Lo que ya está avanzado — 100 %

- Estación DWD 00020 identificada con latitud, longitud y elevación.
- Serie RWS_10 descargada en intervalos de 10 minutos.
- Serie consolidada 2005–2025.
- 21 años calendario utilizables; con año hidrológico octubre–septiembre quedan
  20 años hidrológicos completos (2006–2025).
- Auditoría anual de completitud realizada.
- Valores faltantes y códigos de calidad auditados.
- Intervalos temporales auditados.
- Máximas móviles de 10 min a 24 h generadas.
- Corrección de Weiss generada para intervalos fijos.
- DEM, cobertura del suelo y capas KOSTRA-DWD descargadas.
- Año hidrológico octubre–septiembre definido; quedan 20 años hidrológicos
  completos (2006–2025).
- Climatología mensual, faltantes por mes y justificación espacial preliminar
  generados en `PUNTO_2/datos/punto2/Abtsgmuend_Untergroeningen/control_2_1`.

Archivos principales:

- `station_metadata.csv`
- `data_audit.csv`
- `quality_code_audit.csv`
- `timestamp_interval_audit.csv`
- `ams_precipitation.csv`
- `ams_precipitation_weiss.csv`

### Lo que falta para cerrar el 100 %

1. Definir y justificar el año hidrológico según la estacionalidad local.
2. Revisar si los vacíos coinciden con la temporada de tormentas.
3. Comparar máximos anuales con lluvia diaria del mismo día.
4. Comparar, si se consigue, con una estación vecina o producto regional.
5. Documentar explícitamente la historia de cambios de ubicación de la estación.
6. Finalizar en QGIS la relación estación–microcuenca–outlet.

### Criterio de cierre

La tabla de años aceptados y descartados, el tratamiento de faltantes, las
unidades, los códigos de calidad y la ubicación quedan reproducibles y
justificados.

---

## 2.2. Extremos y ajuste de distribuciones

### Objetivo del apartado

Transformar la serie subdiaria en cuantiles de precipitación extrema con
incertidumbre estadística.

### Lo que ya está avanzado — 95 %

- Series de máximos anuales para 10 min, 30 min, 1 h, 3 h, 6 h, 12 h y 24 h.
- Coherencia entre duraciones comprobada.
- Máximo preliminar de 1 h: 81.26 mm en 2013.
- Mann–Kendall y pendiente de Sen preliminares calculados.
- No se observa tendencia significativa preliminar.
- Se recalcularon máximas para el año hidrológico octubre–septiembre.
- Se ajustaron Gumbel, GEV y log-Pearson III por máxima verosimilitud.
- Se generaron cuantiles preliminares para T = 2, 5, 10, 25, 50 y 100 años.
- Se completaron ajustes por momentos, L-momentos y máxima verosimilitud.
- Se añadieron Kolmogorov–Smirnov y Cramer–von Mises.
- Se generaron intervalos bootstrap GEV-MLE al 95 %.
- Se generaron gráficas de probabilidad y diagrama de razones de L-momentos.
- El bootstrap evidenció inestabilidad en algunos cuantiles T=100, que debe
  discutirse como incertidumbre de extrapolación.

Archivos disponibles: `stationarity_tests.csv` y
`PUNTO_2/datos/punto2/Abtsgmuend_Untergroeningen/extremos_2_2`.

### Trabajo obligatorio pendiente

1. Recalcular máximas usando el año hidrológico elegido.
2. Ajustar Gumbel, GEV y una tercera distribución.
3. Ajustar cada distribución por momentos, L-momentos y máxima verosimilitud.
4. Calcular cuantiles para T = 2, 5, 10, 25, 50 y 100 años.
5. Elaborar gráficas de probabilidad.
6. Aplicar al menos dos pruebas de bondad de ajuste.
7. Elaborar el diagrama de razones de L-momentos.
8. Comparar estabilidad de cuantiles altos y escoger distribución/método.
9. Hacer bootstrap de 95 % para todos los cuantiles.
10. Graficar cómo crece la incertidumbre relativa con T/N.
11. Interpretar la estacionariedad sin afirmar que ausencia de tendencia equivale
    a demostrar invariancia climática.

### Criterio de cierre

La distribución elegida se justifica por pruebas, L-momentos, estabilidad de
cuantiles y coherencia física; no únicamente por el menor estadístico.

---

## 2.3. Curvas IDF

### Objetivo del apartado

Construir curvas intensidad–duración–frecuencia propias y contrastarlas con una
referencia oficial.

### Lo que ya está avanzado — 15 %

- KOSTRA-DWD-2020 descargado para 10 min, 1 h, 6 h y 24 h.
- Duraciones de la serie ya calculadas.
- Eventos extremos disponibles para estimar el periodo de retorno de un evento
  reciente.

### Trabajo obligatorio pendiente

1. Convertir las profundidades de los cuantiles en intensidades mm/h.
2. Construir IDF para al menos dos periodos de retorno.
3. Ajustar una expresión analítica IDF.
4. Reportar parámetros, error y rango de validez.
5. Graficar bandas de incertidumbre.
6. Comparar con KOSTRA-DWD-2020.
7. Explicar diferencias entre lluvia puntual y referencia areal.
8. Estimar el periodo de retorno de un evento intenso reciente con intervalo de
   incertidumbre.
9. Verificar que las curvas no se crucen y que la intensidad disminuya al crecer
   la duración.

### Criterio de cierre

Existe una tabla y una figura IDF reproducibles, con unidades, rangos de
extrapolación, bandas de confianza y comparación oficial.

---

## 2.4. Problemas de diseño

## 2.4 A. Alcantarilla o colector con método racional

### Objetivo del apartado

Diseñar una obra pequeña y cuantificar diámetro, incertidumbre y riesgo.

### Lo que ya está avanzado — 15 %

- Microcuenca D8 preliminar delimitada con SRTM.
- Área preliminar: 0.12315 km².
- DEM validado mediante QGIS Processing.
- Outlet y puntos de control en GeoJSON.

### Bloque pendiente crítico

La revisión visual final del outlet en QGIS no pudo completarse porque la
interfaz gráfica no expuso una ventana controlable. Por eso todavía no se debe
afirmar que el outlet drena hacia una vía, zona urbana o canal.

### Trabajo obligatorio pendiente

1. Abrir el GeoJSON en QGIS y validar el outlet sobre el cauce o estructura de
   drenaje.
2. Si no cumple, mover outlet y repetir la delimitación.
3. Calcular área, longitud y pendiente del cauce principal.
4. Clasificar coberturas y obtener coeficientes C por cobertura.
5. Calcular C ponderado.
6. Calcular tc con al menos tres fórmulas.
7. Elegir T por riesgo, vida útil, consecuencias y práctica de ingeniería.
8. Calcular Qp con el método racional.
9. Dimensionar con Manning y redondear al diámetro comercial superior.
10. Repetir con tc alternativos, C ±20 %, bandas IDF y distribuciones alternativas.
11. Ejecutar Monte Carlo con parámetros bootstrap, C, tc, Manning y pendiente.
12. Reportar probabilidad anual efectiva de falla, riesgo de vida útil y factor de
    seguridad Qc/Qp.
13. Explicar por qué el método racional no se extrapola a cuencas grandes.

### Criterio de cierre

La recomendación reporta diámetro, T, caudal, incertidumbre, supuestos, riesgo
nominal y riesgo efectivo.

## 2.4 B. Tanque de detención

### Objetivo del apartado

Determinar volumen requerido, duración crítica y tamaño de la salida.

### Avance actual — 0 %

Todavía no se han construido hietogramas ni se ha realizado tránsito de
hidrogramas.

### Trabajo obligatorio

1. Seleccionar duración de tormenta como varias veces tc.
2. Construir hietograma de bloques alternos.
3. Repetir con el bloque máximo al inicio, centro y final.
4. Transformar lluvia a hidrograma mediante racional tiempo–área.
5. Definir relación almacenamiento–altura y salida por orificio o vertedero.
6. Transitar por piscina nivelada.
7. Encontrar duración crítica, volumen, altura y tamaño de salida.
8. Comparar hidrogramas trapezoidales contra el hietograma completo.
9. Hacer sensibilidad a T, tc, C, almacenamiento y coeficiente de descarga.

### Criterio de cierre

Se entrega una tabla de diseño y figuras de lluvia, entrada, almacenamiento y
salida para las tres posiciones del pico.

---

## 2.5. Bonificaciones

### Avance actual — 0 %

Las bonificaciones no son necesarias para cumplir el 100 % obligatorio. Solo se
deben iniciar después de terminar 2.1–2.4.

Opciones: mínimo costo esperado, POT, no estacionariedad/cambio climático,
confiabilidad–resiliencia–vulnerabilidad y análisis bivariado con cópula.

No se debe usar una bonificación para compensar un apartado obligatorio
incompleto.

---

## Síntesis del punto 2

### Avance actual — 10 %

La estructura ya está definida, pero faltan resultados de 2.2–2.4.

El cierre debe responder explícitamente:

- ¿Qué lluvia de diseño se escogió y con qué periodo de retorno?
- ¿Qué riesgo nominal y efectivo tiene la obra durante su vida útil?
- ¿Qué incertidumbre domina y cómo se cuantificó?
- ¿Qué supuestos físicos y estadísticos sostienen la recomendación?
- ¿Qué cambia si cambia el clima o la cobertura?
- ¿Qué resultados son observados, modelados o hipótesis?

## Secuencia de trabajo recomendada

1. **Cerrar 2.1:** año hidrológico, temporada de tormentas, metadatos y
   justificación espacial.
2. **Cerrar 2.4 A geométrico:** validar outlet en QGIS y cauce/vía/zona urbana.
3. **Completar 2.2:** distribuciones, pruebas, cuantiles y bootstrap.
4. **Completar 2.3:** IDF propia, KOSTRA, evento reciente e incertidumbre.
5. **Completar 2.4 A hidráulico:** tc, C, Manning, sensibilidad y Monte Carlo.
6. **Completar 2.4 B:** hietogramas, tanque y tránsito.
7. **Redactar síntesis y recomendación.**
8. **Auditar reproducibilidad, ZIP y declaración de IA.**

Cada fase se revisará antes de continuar. Si una comprobación falla, se corrige
el apartado correspondiente y se conserva la evidencia de la corrección.
