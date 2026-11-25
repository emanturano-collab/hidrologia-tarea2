> Nota de actualización: consultar `cierre_final_punto2.md` para los valores finales y la auditoría reproducible. Este archivo conserva el estado previo.

# Cierre técnico del apartado 2.4 y puerta de entrada a 2.5

## Correcciones realizadas

- Se mantuvo el outlet DEM en `48.9181944 N, 9.9123611 E` y se documentó como punto sintético derivado del MDE. La revisión visual confirma que queda sobre el cauce DEM y dentro del polígono, pero no sobre una geometría OSM confirmada.
- Se rerunearon los hietogramas y el tránsito del tanque usando el área real de la geometría propuesta: 24 × 22 m = 528 m².
- El volumen crítico recalculado es **1019.15 m³**, con profundidad máxima **1.93 m**.
- El tanque de 24 × 22 m, 2.0 m útiles y 0.5 m de borde libre tiene 1056 m³; margen **36.85 m³**. Cumple el escenario calculado.
- Se reemplazó la alcantarilla preliminar de 1.20 m por una de **1.50 m**. Capacidad Manning: **7.08 m³/s**; caudal T=25 mediano: 3.57 m³/s; factor de seguridad: **1.98**.
- El Monte Carlo actualizado para la obra de 1.50 m da falla anual 0.0082 y riesgo acumulado a 30 años 0.219. Este riesgo queda reportado explícitamente y no se oculta.

## Pendiente antes de declarar 2.4 cerrado

1. Incluir en el informe la limitación del outlet sintético y decidir si el docente acepta esta hipótesis.
2. Citar las fuentes de los coeficientes de escorrentía por clase WorldCover y declarar suelo/humedad antecedente.
3. Añadir las tablas y figuras finales de caudal, diámetro, incertidumbre y tanque.
4. Revisar la recomendación de riesgo: 21.9 % de falla en 30 años no debe presentarse como riesgo bajo; debe discutirse como limitación del diseño o reducirse con un criterio de seguridad adicional.

## Criterio para iniciar 2.5

Se puede empezar 2.5 como apartado opcional una vez incorporados los cuatro puntos anteriores al informe y cerradas las discusiones finales de 2.2–2.3. Los archivos numéricos principales de 2.4 ya están recalculados y son reproducibles.
