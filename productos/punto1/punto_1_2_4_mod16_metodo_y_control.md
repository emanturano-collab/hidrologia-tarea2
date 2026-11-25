# MOD16A2GF v6.1: extracción de ET real en Racarumi

Producto: `MODIS/061/MOD16A2GF`, bandas `ET` y `ET_QC`, consultado con Earth Engine en el proyecto no comercial `hidrologia-racarumi`.

## Alcance temporal

Se conservaron exclusivamente los dos intervalos de años hidrológicos válidos del balance: 2001-09-01 a 2002-09-01 (AH 2002) y 2003-09-01 a 2023-09-01 (AH 2004--AH 2023). Esto equivale a 252 meses y 21 años hidrológicos. AH 2003 no se incorporó.

## Extracción espacial y calidad

La geometría es la delimitación original `PE_200907_catchment_T1_original.gpkg`, proyectada en la proyección nativa de MODIS. Para cada compuesto se calculó la media ponderada por área de píxeles sobre la cuenca. Los códigos de relleno documentados de ET (>=32761) se excluyeron. `ET_QC` se resumió mediante el bit MODLAND_QC, pero no se usó como máscara adicional: no se aplicó una exclusión de calidad no justificada.

El factor de escala aplicado a ET fue 0.1, con resultado en mm por compuesto. La cobertura válida mínima de los compuestos fue 99.863054 %. No hubo compuestos con cobertura inferior a 95 %.

## Conservación de días

Se consultaron compuestos de guarda a ambos lados de cada periodo para identificar los que cruzan límites mensuales. La duración se obtuvo a partir de la fecha real del siguiente compuesto. Cada total de compuesto se repartió uniformemente entre sus días y se asignó solo al solapamiento correspondiente con cada mes. Es un supuesto explícito de distribución uniforme dentro del compuesto; no es interpolación de datos faltantes. La comprobación final confirmó 968 inicios únicos, 252 de 252 meses con todos sus días y 21 de 21 años hidrológicos con 12 meses. La suma de los meses coincide exactamente con cada total anual.

## Archivos trazables

`datos/punto1/mod16a2gf_racarumi_composites_raw.csv` conserva los compuestos, fechas, duración, ET, área válida, cobertura y resumen QC. Los productos mensuales, anuales y el JSON de control de calidad se generaron desde ese archivo con `codigo/punto1/extraer_mod16a2gf_racarumi.py`.
