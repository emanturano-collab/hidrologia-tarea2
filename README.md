# Tarea 2 · Hidrología · Semestre 202602

Este repositorio se organiza para producir el ZIP exigido por el enunciado. El nombre final del ZIP y de la carpeta raíz debe reemplazar `GNN` y los apellidos por los datos reales del grupo:

`T2_202602_GNN_Apellido1_Apellido2_Apellido3.zip`

La estructura de entrega será:

```text
T2_202602_GNN_Apellido1_Apellido2_Apellido3/
├── README.md
├── T2_202602_GNN_informe.pdf
├── T2_202602_GNN_presentacion.pdf
├── codigo/
│   ├── punto1/
│   └── punto2/
├── datos/
│   ├── punto1/
│   └── punto2/
├── productos/
│   ├── punto1/
│   └── punto2/
└── anexos/
```

Mientras se completa el análisis, este repositorio usa su propia raíz como carpeta de trabajo. Los nombres definitivos se aplicarán al preparar el ZIP.

## Estado de los datos

`datos/punto1/PE_200907/` contiene una copia de los datos seleccionados y procesados de la Tarea 1: estación Racarumi, cuenca Chancay–Lambayeque. Esa cuenca tiene 2363.302 km² y la precipitación disponible es diaria; por ello no cumple directamente los requisitos del punto 2 (microcuenca de 0.1–5 km² y serie subdiaria de lluvia). Se conserva como referencia y para documentar la continuidad con la Tarea 1.

Los datos subdiarios, el DEM y la delimitación de la microcuenca que sí se utilicen en el punto 2 se guardarán en `datos/punto2/`, con metadatos de fuente, versión, unidades, fecha de descarga y procesamiento.

## Convenciones

- Rutas relativas únicamente.
- Archivos internos con ASCII, sin espacios ni tildes.
- No incluir credenciales, claves API ni archivos como `.cdsapirc`.
- Cada resultado del informe debe poder rastrearse a un archivo de `datos/`, un script de `codigo/` y un producto de `productos/`.
