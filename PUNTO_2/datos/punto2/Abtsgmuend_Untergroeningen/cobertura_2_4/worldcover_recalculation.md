# Recalculo WorldCover 2021

Se aplicó una estadística zonal al polígono `microcuenca_abtsgmuend.geojson`
contra el tile oficial `N48E009`. Se contaron los píxeles válidos de la capa
Map y se ponderaron los coeficientes de la tabla `landcover_coefficients.md`.

- Píxeles válidos: **2183**.
- Clases presentes: **3**.
- Coeficiente ponderado recalculado: **C = 0.33239**.
- Sensibilidad global ±20 %: **0.26591–0.39886**.

La tabla completa está en `worldcover_zonal_statistics.csv`.
