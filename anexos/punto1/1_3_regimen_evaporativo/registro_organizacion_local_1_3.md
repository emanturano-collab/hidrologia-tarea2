# Registro de organizacion local del apartado 1.3

Fecha: 2026-11-22. Destino: `tarea 02/`.

## Resultado de la comparacion

Se compararon los archivos directos de codigo, datos procesados, productos y
anexos del apartado 1.3 contra la copia organizada de integracion mediante
SHA-256. Se encontraron 91 archivos directos: 87 son identicos y no hay
archivos faltantes. Por tanto no se copiaron ni duplicaron productos.

La descarga original de humedad de suelo ERA5-Land tambien coincide entre ambas
ubicaciones, con SHA-256
`4117526C0D189BD25C35111C2BBE06CFD36D2297ACF22D72C91B9EAC84ED5501`.

## Conflictos conservados sin sobrescritura

Cuatro scripts tienen el mismo nombre pero contenido distinto. Se conserva la
version ya ubicada en `tarea 02/`, porque sus rutas relativas resuelven desde
la carpeta habitual. No se sustituyo ningun archivo.

| Archivo | SHA-256 destino | SHA-256 copia de integracion |
|---|---|---|
| `run_1_3_regimen_evaporativo.py` | `8D7C2F798F939CE1F1DABEA7F8E629C5FA240FB11ED5BB10B2A7F9C09F4FA0A3` | `48BDD0E471B47BB5FA9535100131D4ADDFFD2C9F7B868180255737BBDDF7983B` |
| `02_humedad_suelo/process_1_3_2_humedad_suelo.py` | `B5DD8390ADFCBD482978B96E1D88E793A6CF79B15B3CC0CF6C213A1421BA66DF` | `EB542535F35AE5567DB138EAE5224E909380CDF28BB6CB91649CD97E430FE0AB` |
| `03_budyko/build_1_3_3_evidencia_documental.py` | `8D26FFC580E72444914641F43B1363804C40CAFBE5A966F893B344AF4DBD31AA` | `BBDDD0DD0E62D4EC75DF483B6475C230BF321A7D7B2D664AEF932FB9920635B7` |
| `06_integracion_1_2_pacho/run_1_3_integracion_ET_real.py` | `54ECE05BA3D89689F9FFA629C7F51E7BFC7C7C9E15CBDB037C735CDD139A64B5` | `F04ABAEE0140ABF01C76D16DF0ADCB4498D7083822163DB34F2B98C662955431` |

## Dependencias de procedencia externa

Los resultados integrados de ET real, GLEAM, MOD16 y radiacion neta conservan
las dependencias minimas ya presentes en
`datos/punto1/originales/1_2_intercambio_pacho/`. No se copio, modifico ni
reorganizo la carpeta de Pacho. Su procedencia registrada es la rama
`punto-1.2`, commit `588ff16b91d5c3533dc7077e72cd809bf3f20768`.

## Controles realizados

- Los seis scripts Python del 1.3 compilan sintacticamente.
- Las figuras propias de 1.3 conservan pares PNG y PDF.
- Los productos se mantienen en las rutas oficiales de codigo, datos,
  productos y anexos.
- No se ejecutaron calculos, descargas ni operaciones Git.

## Alcance conservado

La ETo FAO-56 usada conserva 90.1264 % de cobertura espacial. Permanecen
documentadas las cinco horas UTC faltantes para completar 2023-08-31 local,
las limitaciones de almacenamiento y regulacion, las diferencias entre GLEAM y
MOD16, y el caracter descriptivo de la relacion complementaria.
