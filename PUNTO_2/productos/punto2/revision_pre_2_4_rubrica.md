# Auditoría previa al diseño 2.4 A y 2.4 B

## Dictamen general

La base de datos y el análisis de lluvia están suficientemente avanzados para
comenzar el diseño, pero **el punto 2 completo todavía no cumple al 100 % la
rúbrica**. El diseño debe ejecutarse con una geometría de outlet validada y con
incertidumbres explícitas. Los cálculos provisionales de 2.4 no deben presentarse
como resultados finales.

## Estado por apartado

| Apartado | Estado | Evidencia | Riesgo pendiente |
|---|---|---|---|
| 2.0 | Base metodológica sólida | Ecuaciones, unidades, signos y supuestos | Integrar al informe y citar fuentes completas |
| 2.1 | Cerrado | 20 años hidrológicos, QC y año octubre–septiembre | La cartografía del outlet se conserva para 2.4 |
| 2.2 | 95 % | 3 distribuciones, 3 métodos, 2 pruebas, bootstrap y figuras | Bootstrap T=100 muy inestable; requiere discusión y selección final |
| 2.3 | 75 % | IDF GEV-MLE, KOSTRA y evento reciente | Falta cerrar bandas/selección y redactar comparación física |
| 2.4 A | 30 % | Cálculo provisional y Monte Carlo de prueba | C, tc, longitud, pendiente, coberturas y outlet aún no definitivos |
| 2.4 B | 20 % | Tránsito provisional de tanque | Falta hietograma definitivo, S(h), salida y duración crítica |

## Revisión contra los criterios de la rúbrica

### Criterio de diseño e incertidumbre — 24 %

**No cumplido todavía.** Falta entregar una recomendación final con periodo de
retorno, riesgo nominal y efectivo, fuentes de incertidumbre ordenadas y
supuestos físicos. El Monte Carlo existente es únicamente una prueba provisional.

### Calidad de datos y metodología — 20 %

**Cumplimiento fuerte para la lluvia.** La fuente, duración, faltantes, códigos,
ventanas, año hidrológico y corrección de Weiss están documentados. Para cerrar
este criterio durante 2.4 todavía deben documentarse las fuentes de C, tc,
Manning, pendiente y geometría del tanque.

### Resultados y cálculos — 12 %

**Parcial.** Existen resultados estadísticos e IDF preliminares, pero todavía no
hay un caudal, diámetro, volumen o tamaño de salida definitivos con unidades,
bandas y comprobaciones independientes.

### Reproducibilidad y entrega — 12 %

**Parcial alto.** Los datos originales, derivados y scripts están en el
repositorio. Antes del ZIP final faltan un README de ejecución desde cero,
versiones de dependencias, prueba limpia y comprobación de rutas relativas.

### Comunicación y transparencia de IA — 6 %

**Pendiente de integración en el informe.** Debe incluirse la declaración de IA,
herramientas/versiones, tareas realizadas, verificaciones, correcciones y aporte
de cada integrante.

## Condiciones para iniciar 2.4

Se puede iniciar el diseño como análisis controlado, pero se deben cumplir estas
condiciones antes de congelar resultados:

1. Fijar el outlet sobre un cauce o estructura de drenaje y recalcular la
   microcuenca si cambia el polígono.
2. Medir longitud y pendiente del cauce principal desde el DEM validado.
3. Obtener coberturas y justificar C o CN por fuente.
4. Elegir distribución IDF definitiva considerando ajuste y bootstrap.
5. Registrar cada supuesto provisional con una etiqueta que impida confundirlo
   con un dato observado.

## Decisión

La revisión permite comenzar 2.4 A y 2.4 B **solo como diseño reproducible con
supuestos visibles**. La recomendación final de ingeniería quedará pendiente de
la validación geométrica y de la sustitución de supuestos provisionales.
