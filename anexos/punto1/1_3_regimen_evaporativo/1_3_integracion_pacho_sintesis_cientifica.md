# Integración 1.2 de Pacho con 1.3 — síntesis científica

## Datos integrados y periodo común

Se integraron GLEAM4.3a y MOD16A2GF como ET real mensual, junto con radiación neta
real de superficie de ERA5-Land (`SSR + STR`). El periodo común es AH 2002 y AH
2004–AH 2023: 252 meses y 21 años hidrológicos completos. ETo FAO-56 se conserva
como demanda atmosférica preliminar con cobertura espacial de 90.1264 %.

## Interpretación prudente

ET/ETo y ET/P se presentan por producto y no se promedian como si fueran una
observación. FE es `ET/(Rn/lambda)` en escala mensual; no se reemplazó por ET/ETo.
El ajuste segmentado de FE frente a humedad es exploratorio y no constituye un
umbral físico crítico sin validación independiente y evaluación de resolución.

En Budyko se usan ET de productos para los puntos anuales, conforme a la guía.
Por tanto no se trata P−Q como ET anual. El contraste P−Q queda como diagnóstico
condicionado a ΔS, regulación, extracciones y trasvases; estos factores permanecen
en la interpretación documental del numeral 1.3.3.

La relación ET–demanda se evalúa con terciles de lluvia, ET de cada producto y ETo
FAO-56. Las correlaciones son descriptivas: no demuestran causalidad ni la relación
complementaria por sí solas.

## Resultados clave

- La clasificación explícita de ET/ETo medio de GLEAM y MOD16 identifica enero–mayo
  como meses de agua relativamente disponible/limitados por energía; junio, octubre,
  noviembre y diciembre como transición; julio–septiembre como limitados por agua.
  La clasificación es consistente con la fase húmeda de enero–abril y la fase seca
  de junio–septiembre de Tarea 1, aunque mayo se comporta como transición pluvial.
- Con PISCOp, ET mensual excede P en mayo–septiembre para GLEAM y mayo–agosto para
  MOD16. Esto es compatible con liberación de almacenamiento, aportes/regulación,
  desfases o sesgo de productos; no cuantifica ninguno de esos mecanismos.
- FE media es 0.427 (GLEAM) y 0.460 (MOD16); sus correlaciones Pearson con humedad
  radicular son 0.920 y 0.909, respectivamente. Los quiebres segmentados quedan como
  diagnósticos exploratorios, no como umbrales críticos.
- Con PISCOp, GLEAM da `φ=1.082`, `ET/P=0.671`, `ω=2.284` y distancia a Budyko de
  0.030; MOD16 da `ET/P=0.720`, `ω=2.594` y distancia 0.080. IMERG genera ET/P>1;
  por ello no admite ajuste Fu y se conserva solo como sensibilidad de precipitación.
- En terciles PISCOp, ambos productos muestran ET mayor en años húmedos y ETo menor
  en dichos años; la relación es descriptiva y no establece causalidad.

## Estado de cumplimiento

- 1.3.1: completado preliminarmente con dos productos ET y criterios explícitos.
- 1.3.2: completado preliminarmente para FE y humedad; el supuesto umbral sigue
  siendo exploratorio.
- 1.3.3: actualizado con ET de productos; falta cierre de ΔS y operación.
- 1.3.4: elasticidad teórica recalculada por producto; comparación empírica con
  incertidumbre existente, sin atribución causal.
- 1.3.5: comparación descriptiva completada con ambos productos; no causal.
