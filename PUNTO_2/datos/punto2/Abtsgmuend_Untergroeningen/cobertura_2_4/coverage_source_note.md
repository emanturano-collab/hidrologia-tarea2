# Trazabilidad de cobertura

Se incorporó el raster original **ESA WorldCover 2021 v200**, tile `N48E009`,
que cubre 9–12° E y 48–51° N, incluyendo la estación y la microcuenca.

- Producto: ESA WorldCover 10 m 2021 v200, capa Map.
- CRS: EPSG:4326.
- Resolución: 0.0000833333° por píxel (aproximadamente 10 m).
- URL oficial: `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N48E009_Map.tif`.
- Metadatos: `worldcover_metadata.json`.
- Integridad: `worldcover_sha256.txt`.
- Tamaño: 94,851,935 bytes.
- SHA-256: `9f422e4da7ed4c34154983575660a5a26f2d5fb7935fa46f3551af45d5b6c1d3`.

Las proporciones usadas para el cálculo de (C) se conservan en
`worldcover_summary.csv` y `weighted_runoff_coefficient.csv`. La tabla deberá
recalcularse mediante zonal statistics sobre este raster y el polígono de la
microcuenca antes de la entrega final.
