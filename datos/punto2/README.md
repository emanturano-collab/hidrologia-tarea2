# Datos del punto 2

La estación de diseño es DWD 00020 (Abtsgmünd–Untergröningen, Alemania),
ubicada en 48.9219 N, 9.9129 E, con precipitación cada 10 minutos. El periodo
calendario analizado es 2005–2025 y los años hidrológicos completos usados en
extremos son 2006–2025.

La microcuenca sintética delimitada con SRTM tiene 0.123154 km², cauce principal
de 382.69 m y outlet en 48.9181944 N, 9.9123611 E. La estación está fuera del
polígono y se usa como referencia regional de lluvia.

## Evidencias principales

- `abtsgmuend_precipitation_10min.csv`: serie consolidada local.
- `control_2_1/`: climatología, años hidrológicos, faltantes, códigos de calidad,
  intervalos temporales y revisión espacial.
- `extremos_2_2/`: máximos anuales, ajustes, bootstrap y pruebas de ajuste.
- `idf_2_3/`: IDF GEV-MLE, parámetros de potencia y comparación KOSTRA.
- `cobertura_2_4/`: tabla de cobertura y coeficiente ponderado.
- `diseno_2_4/`: escenarios, geometría de alcantarilla y tanque.
- `bonificacion_2_5_pot/`: POT, sensibilidad de umbral y comparación con GEV.

El raster WorldCover original no está incluido en esta copia; la tabla de
cobertura está reconstruida desde los porcentajes documentados en el cierre de
2.4 y esa limitación debe declararse en la entrega.
