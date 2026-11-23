# Apartado 2.4 — avance provisional

Se generaron cálculos iniciales para los problemas A y B usando el área y la
trayectoria principal derivadas del DEM (`A=0.12315 km2`, `L=382.69 m`,
`S=0.12543`). La cobertura WorldCover ya fue extraída y produce `C=0.334`
ponderado. Siguen siendo provisionales `CN=75`, `n=0.013` y la pendiente de
tubería 0.01, hasta seleccionar la estructura de drenaje y justificar suelo y
humedad antecedente.

Archivos: `PUNTO_2/datos/punto2/Abtsgmuend_Untergroeningen/diseno_2_4/`.

- Problema A: comparación de tres tc, caudal/diámetro provisional, sensibilidad
  Monte Carlo de 5000 iteraciones y riesgo de vida útil.
- Problema B: hietograma simplificado, entrada/salida del tanque y volumen
  provisional.

Los resultados sirven para probar el código y detectar errores de unidades, pero
no deben ir al informe final como recomendación de ingeniería hasta cerrar la
geometría y las coberturas.
