# Plan de cierre hacia nota 5.0 — dos fases

Este plan convierte la matriz de evaluación en dos fases de trabajo. La primera
cierra todos los requisitos obligatorios; la segunda desarrolla las
bonificaciones y hace una auditoría final de calidad. Los bonos solo se suman
si el trabajo escrito obligatorio queda en 3.0 o más y tienen un tope total de
`+0.5`.

## Fase 1 — Cierre obligatorio y nota base excelente

**Meta:** elevar el trabajo escrito obligatorio desde el estado actual
estimado de `3.18/5.0` a aproximadamente `4.5–4.8/5.0`, dejando una versión
completa y defendible antes de intentar los bonos.

### 1. Integrar el punto 1 (26 %)

- Sustituir el espacio reservado por el análisis real de evapotranspiración de
  la cuenca PE_200907/Racarumi.
- Incluir demanda, evapotranspiración real, limitantes mensuales, comparación
  de métodos, posición en Budyko, atribución del cambio y proceso propio de la
  cuenca.
- Incorporar bibliografía y explicaciones alternativas, no solo resultados.

**Aceptación:** el criterio de interpretación física tiene una sección
completa, figuras y citas, y cada integrante puede explicarlo oralmente.

### 2. Cerrar 2.0–2.1

- Añadir una tabla de decisión del periodo de retorno: vida útil, riesgo
  aceptable, consecuencias de falla y comparación con Chow et al. (1988).
- Mostrar criterios de año válido, años descartados, completitud anual y
  sensibilidad de cuantiles.
- Mantener visibles estación, coordenadas, resolución de 10 minutos, metadatos,
  códigos de calidad, Weiss, checksum y rutas relativas.

**Aceptación:** un lector puede reconstruir de dónde sale cada año válido y por
qué se eligió `T=25` años.

### 3. Perfeccionar 2.2–2.3

- Presentar una tabla compacta de cuantiles para `T=2, 5, 10, 25, 50, 100`
  por distribución, método y duración disponible; conservar el CSV completo.
- Añadir explícitamente la justificación conjunta de KS/CvM, L-momentos,
  estabilidad de cola y selección GEV-MLE.
- Mostrar bandas de incertidumbre de IDF para al menos dos retornos y declarar
  parámetros, RMSE/MAE/R² y rango válido.
- Explicar KOSTRA como comparación puntual–areal, no como sesgo puro.
- Mantener separado evento extremo, anomalía estadística y tendencia.

**Aceptación:** las figuras y tablas visibles responden directamente a cada
inciso 2.2 y 2.3 del enunciado.

### 4. Perfeccionar 2.4A–2.4B

- Añadir suelo, humedad antecedente y el efecto de `C` en la recomendación.
- Documentar riesgo aceptable, consecuencias y práctica de diseño.
- Ordenar la sensibilidad por efecto sobre el diámetro (`C`, IDF, `tc`,
  Manning, pendiente y distribución).
- Incorporar una tabla que compare hidrogramas trapezoidales con el hietograma
  de bloques alternos para cada posición del pico.
- Explicar cuantitativamente la ley de salida y el tamaño adoptado del orificio.
- Conservar explícita la limitación: el outlet es sintético, no un aforo ni una
  obra existente.

**Aceptación:** se reportan valor, incertidumbre, supuestos y limitaciones de
la alcantarilla y del tanque, no solamente el diámetro y el volumen finales.

### 5. Entrega base

- Sustituir `G00` por el número oficial del grupo.
- Integrar el punto 1 en el ZIP y conservar `codigo/`, `datos/`, `productos/` y
  `anexos/` con rutas relativas.
- Ejecutar desde una carpeta limpia, compilar el PDF, renderizar todas las
  páginas y validar el ZIP.

**Puerta de fase:** no iniciar bonos hasta obtener auditoría limpia 10/10,
PDF sin errores visuales, citas APA 7 completas y nota obligatoria estimada
mayor o igual a `4.5`.

## Fase 2 — Bonificaciones 2.5.1–2.5.5 y defensa final

**Meta:** obtener hasta `+0.5` adicional y dejar preparada la defensa oral.

### 2.5.1 Diseño de mínimo costo esperado (+0.2)

- Usar la IDF del punto 2 para varios `T`.
- Calcular costo anualizado de obra con `FRC`, daño anual esperado y `T`
  óptimo.
- Comparar el `T` óptimo con el elegido por riesgo.
- Repetir sensibilidad para `Dmax/2`, `Dmax` y `2Dmax`, y para la tasa de
  descuento.

**Producto:** tabla de costos, curva costo–T, intervalo/sensibilidad y decisión
ingenieril argumentada.

### 2.5.2 Excedencias sobre umbral (+0.1)

- Mantener POT con umbral justificado y declustering documentado.
- Compararlo con AMS mediante la relación de Langbein (1949).
- Reportar incertidumbre GPD y sensibilidad del umbral.

**Producto:** tabla POT–AMS–Langbein, figura de comparación y referencia
metodológica verificable. Si el registro fuese de 10–19 años sería obligatorio,
pero aquí se presenta como bono porque hay más de 20 años válidos.

### 2.5.3 No estacionariedad y cambio climático (+0.1)

- Ajustar GEV con localización dependiente del tiempo o temperatura, o aplicar
  el escalamiento de 7 % por grado con referencia a Westra et al. (2014).
- Recalcular diámetro del problema A y periodo de retorno efectivo del diseño.

**Producto:** escenario base–calentado, cambio de diámetro, cambio de riesgo y
discusión de supuestos.

### 2.5.4 Confiabilidad, resiliencia y vulnerabilidad (+0.1)

- Convertir la serie subdiaria completa a caudal mediante racional tiempo–área.
- Calcular frecuencia de excedencia de la alcantarilla, duración hasta la
  recuperación y magnitud del exceso.
- Aplicar las definiciones de Hashimoto et al. (1982).

**Producto:** serie de desempeño, métricas R–Res–V y figura de eventos de falla.

### 2.5.5 Análisis bivariado (+0.1)

- Ajustar una cópula entre intensidad y duración.
- Calcular periodos de retorno conjuntos para eventos de diseño.
- Comparar el resultado con el análisis univariado IDF.

**Producto:** selección de cópula justificada, gráfico de dependencia, tabla de
retornos conjuntos e incertidumbre.

### 6. Auditoría final y presentación

- Actualizar APA 7 para cada método nuevo.
- Ampliar la declaración de IA con herramientas, tareas, verificaciones,
  correcciones y contribución individual.
- Recalcular la matriz, aplicar el tope de `+0.5` y congelar resultados.
- Preparar una exposición de 10 minutos más 5 minutos de preguntas: datos,
  GEV-MLE, riesgo, incertidumbre, alcantarilla, tanque, limitaciones y bonos.

**Criterio de cierre:** el informe debe responder explícitamente qué lluvia se
escogió, con qué periodo de retorno, qué riesgo tiene la obra, cuál es la mayor
fuente de incertidumbre y qué cambia si cambia el clima o la cobertura.

## Resultado esperado

Si se completa la Fase 1 y se integran correctamente ambos puntos, el trabajo
obligatorio puede ubicarse en el rango `4.5–4.8`. Si además se documentan con
rigor los cinco bonos de la Fase 2, la nota final puede alcanzar `5.0` por el
tope de bonificaciones.
