# Revisión de 2.4 antes de avanzar

## Dictamen

El apartado 2.4 **todavía no cumple al 100 % la rúbrica**. Los archivos actuales
son un avance técnico reproducible, pero no una recomendación final de ingeniería.
Por tanto, no conviene pasar todavía a la síntesis ni a las bonificaciones.

## Cumplimientos actuales

- Área de la microcuenca dentro de 0.1–5 km².
- Longitud y pendiente preliminares derivadas del DEM.
- Cobertura WorldCover extraída y C ponderado calculado.
- Tres tiempos de concentración comparados.
- Manning, diámetro comercial y capacidad calculados.
- Sensibilidad preliminar de C, Manning y pendiente.
- Geometría preliminar de alcantarilla y tanque documentada.

## Incumplimientos o riesgos pendientes

1. **Outlet:** el punto final todavía no está demostrado sobre un cauce o
   estructura de drenaje. Esto es obligatorio en 2.4.
2. **Tiempo de concentración:** SCS-lag produce 0.48 min, un valor que requiere
   revisar fórmula, unidades y aplicabilidad antes de usarlo.
3. **Coeficiente C:** las clases de cobertura son observadas, pero los C por
   cobertura siguen siendo supuestos; falta documentar fuente y considerar suelo
   y humedad antecedente.
4. **Riesgo efectivo:** el Monte Carlo actual es exploratorio y debe muestrear
   consistentemente bootstrap, C, tc, Manning y pendiente.
5. **Tanque:** los escenarios de 30, 60 y 90 min producen el mismo almacenamiento
   máximo; esto indica que el tránsito/hietograma todavía no discrimina la
   duración crítica y debe corregirse.
6. **Geometría:** el diámetro 1.20 m y el tanque 20 x 22 x 2.0 m son propuestas
   preliminares, no resultados finales.

## Correcciones iniciadas

- Se corrigió la fórmula SCS-lag a unidades pies/horas; el resultado pasó de
  0.48 min a aproximadamente 9.44 min.
- Se corrigió el hietograma de bloques alternos para usar profundidades
  acumuladas `P=i(d)d`, evitando incrementos negativos.
- El tránsito ahora distingue posiciones del pico. El escenario más exigente es
  30 min con el pico al final: 998.66 m³.
- La geometría preliminar del tanque se actualizó a 24 m × 22 m × 2.0 m útiles,
  0.5 m de borde libre y 1056 m³, con margen de 57.34 m³.

## Decisión

No se debe declarar 2.4 cerrado ni pasar a la síntesis. La siguiente fase debe
ser **corregir y validar 2.4**, en este orden: outlet, tc, C documentado, riesgo
Monte Carlo y tránsito del tanque. Solo después se podrá cerrar el punto 2 y
redactar la recomendación final.
