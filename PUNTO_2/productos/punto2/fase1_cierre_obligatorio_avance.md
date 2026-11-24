# Fase 1 — avance de cierre obligatorio

## Completado en esta iteración

- El informe ahora incorpora el contexto verificable de PE_200907/Racarumi:
  coordenadas, área, periodos de precipitación, caudal y temperatura, y sus
  auditorías de faltantes.
- Se añadió en 2.0 una explicación explícita de vida útil de 30 años, T=25,
  riesgo nominal y riesgo efectivo Monte Carlo.
- Se añadió en 2.1 una tabla visible de resolución, completitud, años válidos,
  códigos, Weiss y trazabilidad.
- Se añadió en 2.4A una discusión explícita de suelo, humedad antecedente,
  sensibilidad y la limitación del outlet sintético.
- Se añadió en 2.4B una tabla de comparación entre hietogramas y escenarios
  trapezoidales, junto con la ley de salida y el tránsito.
- El PDF se recompiló y conserva la nomenclatura 2.0–2.5.

## Bloqueadores que requieren archivos del grupo

- La carpeta compartida de punto 1 no contiene la tabla maestra mensual ni los
  productos de ETo, Budyko, atribución y proceso propio. El informe los deja
  declarados como pendientes para no inventar resultados.
- La tabla completa de cuantiles de 2.2 por todas las duraciones todavía está
  en CSV; el PDF muestra la tabla principal de 10 minutos.
- La comparación trapezoidal–hietograma de 2.4B tiene una tabla de control,
  pero requiere completar los volúmenes de cada escenario desde los CSV de
  tránsito antes de afirmar cierre perfecto.
- El ZIP sigue usando `G00` hasta conocer el número oficial del grupo.

## Puerta de cierre

La fase no puede declararse 100 % cerrada hasta incorporar los productos reales
del punto 1 y reemplazar los marcadores del ZIP. Los restantes pendientes son
trazables y están separados de los resultados ya verificados.
