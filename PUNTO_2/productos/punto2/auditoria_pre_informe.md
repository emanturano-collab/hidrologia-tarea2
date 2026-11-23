# Auditoría previa al informe presentable

Este archivo controla el cierre técnico antes de generar el PDF final. No es
el informe de entrega.

## Estado de verificación

| Bloque | Estado | Evidencia |
|---|---|---|
| Datos DWD y metadatos | Cerrado | `station_metadata.csv`, auditorías de calidad |
| Microcuenca y DEM | Cerrado con limitación | `cuenca_resumen.csv`, mapas visuales |
| Outlet | Documentado como sintético | `cierre_2_4_final.md` |
| Extremos 2.2 | Cerrado metodológicamente | `discusion_2_2_2_3_final.md` |
| IDF 2.3 | Cerrado metodológicamente | `discusion_2_2_2_3_final.md` |
| Alcantarilla 2.4A | Recalculada | `geometria_alcantarilla.csv` |
| Tanque 2.4B | Recalculado | `geometria_tanque.csv` |
| Incertidumbre y riesgo | Cerrado con riesgo residual | `cierre_2_4_final.md` |
| Bonificación POT 2.5 | Cerrada | `cierre_2_5_pot.md` |
| Informe integrado | Pendiente | Se hará al final |
| PDF presentable | Pendiente | No iniciar todavía |

## Correcciones que deben revisarse antes del informe

1. Confirmar que todas las tablas usen las mismas unidades: mm, mm/h, m³/s,
   km² y minutos.
2. Confirmar que el diámetro final de 1,50 m y el tanque 24 × 22 m coincidan en
   todos los archivos y no queden valores preliminares de 1,20 m o 20 × 22 m.
3. Mantener separadas las estimaciones GEV-MLE y POT; POT es una bonificación y
   no modifica automáticamente la IDF de diseño.
4. Revisar que el riesgo de 21,9 % a 30 años aparezca como riesgo residual y no
   como una validación de seguridad.
5. Mantener visible la limitación del outlet sintético en mapas, resultados y
   conclusiones.
6. Ejecutar nuevamente los scripts principales en el orden documentado y
   conservar sus salidas finales.

## Criterio de inicio del informe

El informe presentable solo se iniciará cuando los seis puntos anteriores estén
verificados y no existan discrepancias entre CSV, Markdown, mapas y scripts.
