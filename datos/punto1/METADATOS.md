# Datos Punto 1

- Fuente: m?ltiples or?genes trazados en `anexos/manifiesto_organizacion.csv`.
- Versi?n: [COMPLETAR por conjunto].
- Unidades: [COMPLETAR por variable].
- Fecha de descarga: [COMPLETAR cuando no conste en cabeceras].
- Procesamiento: conservar contenido byte a byte; transformaciones descritas por los scripts asociados.
- Cobertura espacio-temporal: [COMPLETAR por conjunto].
- Archivos inventariados en esta carpeta y subcarpetas: 128.

`productos/punto1/1_1_a/fao56_eto_diaria_por_celda_preliminar_90pct.csv` es una salida preliminar al 90 %.


## GLEAM v4.3a (verificado por cabecera)

- Fuente: GLEAM v4.3a, archivos `E_YYYY_GLEAM_v4.3a_MO.nc`.
- Variable: `E`; unidades: [COMPLETAR desde atributo `units`].
- Periodo disponible: 2001?2023, 12 meses por archivo.
- Cobertura: global, latitud ?89.95 a 89.95 y longitud ?179.95 a 179.95; malla 1800 ? 3600.
- Scripts que lo leen: `procesar_gleam43a_racarumi.py`, `03_procesar_gleam_por_bandas.py` y validadores asociados.
- Estado: base global sin recorte. No se gener? ning?n recorte; decisi?n de inclusi?n pendiente.
