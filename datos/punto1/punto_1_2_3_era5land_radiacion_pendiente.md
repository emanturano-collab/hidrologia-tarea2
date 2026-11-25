# Radiacion neta real ERA5-Land

Los archivos `ssr` y `str` aun no se han descargado ni sustituido por datos alternativos.

El script `../../codigo/punto1/punto_1_2_3_radiacion_neta_era5land.py` solicita ambos campos a CDS para 2000-09 a 2023-08. Reutiliza la delimitacion y los 33 pesos espaciales originales de la Tarea 1 conservados en esta carpeta.

Los meses 2022-09 a 2023-08 se solicitan mediante `monthly_averaged_reanalysis_by_hour_of_day` a las 00:00, conforme a la correccion oficial de ECMWF para los campos acumulados afectados. El script no escribe el producto procesado si falta alguna celda ponderada o si no se obtienen los 276 meses solicitados.
