# Tarea 2 de Hidrología

## Integrantes

- Andrés Francisco Idrobo Hidrobo
- Jeyson Cristian Javier Irpanoca
- Enmaly Aleli Manturano Grajeda

El grupo no tiene número asignado; por eso el nombre de la entrega omite el segmento `GNN`.

## Estructura de la entrega

- `codigo/`: scripts reproducibles de los puntos 1 y 2.
- `datos/`: entradas seleccionadas, recortadas cuando corresponde, y metadatos.
- `productos/`: tablas, series, mapas y figuras producidos.
- `anexos/`: trazabilidad, guía y verificaciones.

La raíz no contiene carpetas adicionales ni archivos comprimidos. El informe y el dashboard/presentación se preparan después de esta organización.

## Entorno y credenciales

- Versión mínima documentada: Python **3.9**.
- Intérprete usado en la verificación: Python 3.14.10.
- Dependencias: `codigo/requirements.txt` (incluye `reportlab`, `Pillow` y `GDAL` para el import `osgeo`).
- Los scripts GLEAM leen `GLEAM_SFTP_PASSWORD` desde una variable de entorno. No se incluyen claves.

## Punto 1

Se conservaron los datos mínimos de Tarea 1 y la trazabilidad en `anexos/punto1/`. La corrida aislada de 1.3 reprodujo sus tablas con tolerancia `1e-9`. Los insumos globales deliberadamente excluidos se indican abajo; no se sustituyeron.

## Punto 2

- Fuente definitiva: `github:punto-2@9741a85` (`9741a85de7391396d981aee4826836a7ac21bb07`). No se incorporó material exclusivo de `main`.
- Serie DWD: 2005-01-01 a 2025-12-31, 1.104.480 filas, SHA-256 `c34541e60ce7dbe952e8a814192a51707dc8986ac758195c810c53c15764773a`.
- DEM: recorte de entorno sin remuestreo y recorte exacto por microcuenca, ambos descomprimidos. No se entrega el `.hgt.gz`.
- Metadatos por archivo: `datos/punto2/METADATOS.md`.
- Trazabilidad del bono: `anexos/punto2/trazabilidad_bonificaciones.csv`.
- 2.4 B permanece **no cerrado**. Faltan los hidrogramas trapezoidales, su comparación de volumen y el pico preurbanización con el mismo T. La evidencia y las cifras están en `productos/punto2/verificacion_cierre_2_4_B.md`.
- El bono 2.5 POT se conservó y regeneró. La serie completa 2005-2025 produjo 1.491 picos declusterizados, frente a 1.523 en el producto previo que incluía el tramo parcial de 2004.

### Comparación de productos de Punto 2

- 44 CSV coincidieron numéricamente con tolerancia `1e-9`.
- 148 archivos binarios fueron idénticos y 5 JSON coincidieron semánticamente.
- Las diferencias numéricas se concentran en POT y auditorías temporales por el recorte correcto a 2005-2025.
- Las figuras regeneradas pueden diferir byte a byte por metadatos de renderizado.
- `extraer_cobertura_2_4.py` no se ejecutó porque falta el raster ESA exacto; se conservaron sus derivados de la rama sin marcarlos como reproducidos.

## Insumos no incluidos

| Ruta exacta o patrón | Razón y efecto |
|---|---|
| `datos/punto1/gleam4_3a_raw/E_2001_GLEAM_v4.3a_MO.nc` … `E_2023_GLEAM_v4.3a_MO.nc` | Globales no incluidos; se entrega el recorte de cuenca y periodo. El reprocesamiento desde los globales queda deshabilitado con error explícito. |
| `datos/punto1/originales/era5land_humedad_suelo/ERA5_Land_Racarumi_Humedad_Suelo_1981_2023.zip` | No localizado. Bloquea la regeneración de 1.3.2; no se sustituyó. |
| `datos/punto2/Abtsgmuend_Untergroeningen/ESA_WorldCover_10m_2021_v200_N48E009_Map.tif` | No localizado. Bloquea la regeneración independiente de cobertura y coeficiente C de 2.4; el script falla con mensaje explícito. |

## Verificación final

- `py_compile`: 69/69 scripts sin errores.
- Verificador: `anexos/verificador_rutas_final.csv`.
- Lecturas estáticas: 136 existentes; 31 dinámicas controladas; dos faltantes deliberados de Punto 1 y un insumo faltante de Punto 2 (el raster ESA; su recorte es una salida generada por el mismo script).
- Grep en código: 0 rutas absolutas, 0 referencias a perfiles de usuario, descargas o carpetas de trabajo y 0 rutas históricas de Tarea 1.
- No hay `.zip`, `.gz`, `.rar`, `.7z`, clones, worktrees ni `.git` dentro de la entrega.

## Estado por script

| Script | Estado | Evidencia o razón |
|---|---|---|
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/build_fao56_preliminar_90pct_products.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/build_spatial_inventory_1_1a.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/download_era5land_25_celdas.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/run_fao56_1_1a.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/run_fao56_1_1a_preliminar_90pct.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/verificar_cds_era5land.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/build_1_1b_integrated_status.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_camels_pet_y_balance.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_noaa_ghcnh_station.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_station_vs_era5_chiclayo.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_terraclimate_pet.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_c_metodos_alternativos/run_1_1c_metodos_alternativos.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_1_demanda_atmosferica/1_1_d_explicacion_fisica/run_1_1d_explicacion_fisica.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/02_propagacion_error/run_1_2_2_propagacion_error.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/cierre_punto_1_2_4.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/descargar_gleam43a_mensual.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_2_evapotranspiracion_real/extraer_mod16a2gf_racarumi.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/gleam43a_lote_openssh.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_2_evapotranspiracion_real/inventariar_gleam_sftp.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_2_evapotranspiracion_real/procesar_gleam43a_racarumi.py` | no ejecutado | Los NetCDF globales no se entregan; se conserva el recorte de cuenca y periodo. |
| `codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_fraccion_evaporativa.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_radiacion_neta_era5land.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_techo_energetico.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_2_evapotranspiracion_real/validar_gleam43a_local.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_3_regimen_evaporativo/02_humedad_suelo/process_1_3_2_humedad_suelo.py` | no ejecutado | Falta la entrada ERA5-Land de humedad del suelo indicada en Insumos no incluidos. |
| `codigo/punto1/1_3_regimen_evaporativo/03_budyko/build_1_3_3_evidencia_documental.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_3_regimen_evaporativo/03_budyko/run_1_3_3_1_3_4_consolidacion.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_3_regimen_evaporativo/05_relacion_complementaria/run_1_3_3_1_3_4_1_3_5_complementos.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_3_regimen_evaporativo/06_integracion_1_2_pacho/run_1_3_integracion_ET_real.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_3_regimen_evaporativo/run_1_3_regimen_evaporativo.py` | ejecutado y reproducido | 6/6 tablas con diferencia máxima 0 (tolerancia 1e-9) y 3/3 PNG idénticos. |
| `codigo/punto1/1_4_cambios_demanda_evaporativa/run_1_4.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_4_cambios_demanda_evaporativa/run_1_4_1_auditoria.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_5_paisaje/01_construir_bandas_altitudinales.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_5_paisaje/02_extraer_mod16_por_bandas.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_5_paisaje/03_procesar_gleam_por_bandas.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_5_paisaje/04_reconstruir_eto_fao56_por_celda_y_banda.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_5_paisaje/05_cierre_tecnico_1_5.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_6_frecuencia/01_descargar_y_evaluar_precipitacion_dwd.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_6_frecuencia/02_descargar_y_calcular_eto_era5land.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/1_6_frecuencia/03_evaluar_temporada_seca.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/1_6_frecuencia/04_verificar_recuperacion_dwd_horaria.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/gleam43a_lote_openssh.py` | solo compilado | Descarga/transferencia no ejecutada; no se guardaron credenciales. |
| `codigo/punto1/organizar_consulta_punto_1_4.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/render_auditoria_1_4_1.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/run_1_4.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/run_bonificacion_budyko_fu.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto1/validar_gleam43a_local.py` | solo compilado | No se ejecutó en esta verificación final. |
| `codigo/punto2/ajustar_2_2.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/ajustar_2_2_completo.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/auditar_pre_informe.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/bonificacion_pot_2_5.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/bootstrap_2_2.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/comparar_kostra_2_3.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/construir_2_3_idf.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/diseno_2_4_provisional.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/extraer_cobertura_2_4.py` | no ejecutado | Falta el raster ESA WorldCover 2021 v200 exacto; el script falla con mensaje explícito. |
| `codigo/punto2/finalizar_2_4.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/geometria_obra_2_4.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/graficar_pot_2_5.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/graficas_2_2.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/mapa_revision_visual.py` | ejecutado | Productos cartográficos regenerados; los binarios no son comparables byte a byte. |
| `codigo/punto2/preparar_2_1.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/preparar_cuenca.py` | ejecutado y reproducido | Área 0,123153988 km², salida y longitud de cauce reproducidas con el recorte SRTM. |
| `codigo/punto2/preparar_lluvia.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/reconstruir_evidencias_finales.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/reconstruir_precipitacion.py` | ejecutado | Serie DWD reconstruida y recortada a 2005-2025; 1.104.480 filas. |
| `codigo/punto2/revisar_lluvia.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/sensibilidad_pot_2_5.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
| `codigo/punto2/validar_contexto_2_1.py` | ejecutado | Ejecutado el 24 de noviembre de 2026; las coincidencias y diferencias se resumen abajo. |
