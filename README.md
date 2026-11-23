# Tarea 2 de Hidrología

El repositorio está organizado en los dos componentes de la tarea:

```text
PUNTO_1/
├── datos/       # Información y productos heredados de la Tarea 1
├── codigo/      # Espacio reservado para los scripts del punto 1
└── productos/   # Resultados del punto 1

PUNTO_2/
├── datos/       # Datos DWD, DEM, coberturas y resultados numéricos
├── codigo/      # Scripts de preparación, análisis y diseño
├── productos/   # Productos metodológicos y revisiones de la rúbrica
├── informe/     # Fuentes LaTeX del informe
├── output/      # PDFs generados
├── anexos/      # Material complementario
└── GUIA_PASO_A_PASO_PUNTO2.md
```

El punto 1 conserva la información de la cuenca PE_200907 (Racarumi,
Chancay–Lambayeque) trabajada en la Tarea 1. El punto 2 utiliza de forma
independiente la estación DWD 00020 y la microcuenca Abtsgmünd–Untergröningen.

Las bases brutas de gran tamaño, cachés y archivos temporales se mantienen
fuera del control de versiones mediante `.gitignore`. Los datos procesados,
scripts, figuras, tablas y documentación necesarios para reproducir el
análisis sí están organizados dentro de `PUNTO_1/` y `PUNTO_2/`.

## Informe

El informe LaTeX se encuentra en
`PUNTO_2/informe/informe_tarea2.tex`. Los PDFs generados están en
`PUNTO_2/output/pdf/`.
