# 1.4.3. La paradoja del tanque: interpretación científica

## Alcance y evidencia disponible

El análisis se refiere a la demanda evaporativa atmosférica de Racarumi durante 1981--2022. La ETo FAO-56 tiene una pendiente de Sen de **+1.14 mm/año por año** (p = 0.0026), mientras que Thornthwaite presenta **+0.57 mm/año por año** (p = 0.00048). Por tanto, ambos métodos muestran un incremento estadísticamente significativo de la demanda evaporativa, aunque no con la misma magnitud.

No se identificaron registros locales de evaporación de tanque en los datos, productos ni anexos disponibles del proyecto. En consecuencia, la paradoja del tanque se discute aquí como marco conceptual; no se realiza una prueba observacional de tendencia de evaporación de tanque para Racarumi.

## Comparación de FAO-56 y Thornthwaite

FAO-56 Penman--Monteith estima ETo mediante temperatura, humedad atmosférica, velocidad del viento y radiación solar. Thornthwaite emplea principalmente la temperatura media mensual y una corrección por duración del día. La pendiente mayor de FAO-56 es coherente con que incorpora el incremento de radiación y el efecto de la humedad sobre el déficit de presión de vapor, procesos que Thornthwaite no representa explícitamente.

La diferencia entre pendientes no demuestra que uno de los métodos sea una observación directa de la evaporación real. Expresa, en cambio, que sus supuestos y forzantes son diferentes. Thornthwaite es un indicador térmico; FAO-56 es físicamente más sensible a los controles radiativos y aerodinámicos de la demanda atmosférica.

## Evidencia de los forzantes atmosféricos

La atribución de primer orden basada en FAO-56 reconstruye una tendencia de +1.210 mm/año por año, cercana a la pendiente directa OLS de +1.163 mm/año por año; el residuo es -0.047 mm/año por año. Las contribuciones estimadas son:

| Forzante | Tendencia observada | Contribución a ETo |
|---|---:|---:|
| Temperatura del aire | +0.018 °C/año | +0.760 mm/año por año |
| Presión real de vapor, ea | +0.00107 kPa/año | -0.127 mm/año por año |
| Viento a 2 m, u2 | +0.00022 m/s/año | +0.008 mm/año por año |
| Radiación solar, Rs | +0.0138 MJ m-2 día-1 año-1 | +0.569 mm/año por año |

El calentamiento y el incremento de radiación explican la mayor parte del aumento de ETo. El aumento de ea reduce parcialmente el déficit de presión de vapor y, por ello, compensa parte de ese aumento. La contribución del viento es prácticamente nula. La compensación por humedad no es suficiente para neutralizar los aportes positivos de temperatura y radiación.

## ¿Existe una paradoja del tanque en Racarumi?

La llamada paradoja del tanque describe situaciones en que la evaporación observada en tanque disminuye aun cuando aumenta la temperatura del aire, normalmente por cambios compensatorios de radiación, viento, humedad o nubosidad. En Racarumi no puede afirmarse ni descartarse empíricamente ese fenómeno porque no hay una serie local de evaporación de tanque disponible.

La evidencia indirecta tampoco apunta a una paradoja de la demanda evaporativa: tanto FAO-56 como Thornthwaite aumentan y la atribución FAO-56 indica un efecto positivo dominante de temperatura y radiación. El efecto negativo de ea existe, pero es menor que la suma de las contribuciones de temperatura y radiación. Por tanto, los resultados disponibles respaldan aumento de la demanda evaporativa atmosférica, no una disminución compensada comparable a la paradoja del tanque.

## Limitaciones y uso correcto de la conclusión

- La ETo FAO-56 representa una cobertura espacial ponderada de **90.1264 %** de la cuenca; no debe interpretarse como cobertura completa.
- Faltan cinco horas UTC para completar el borde local del 31-08-2023. Este análisis usa solamente años completos 1981--2022, por lo que esa omisión no afecta directamente las tendencias aquí reportadas.
- ETo es demanda atmosférica de un cultivo de referencia; no equivale a evapotranspiración real ni a evaporación de tanque.
- La atribución es de primer orden: mantiene los demás forzantes constantes y no prueba causalidad ni representa todas sus interacciones.
- Se necesitaría una serie local, homogénea y con metadatos de evaporación de tanque para evaluar una paradoja del tanque observada.

## Conclusión

Para 1981--2022 hay evidencia de aumento de la demanda evaporativa en Racarumi. FAO-56 y Thornthwaite muestran tendencias positivas, con mayor magnitud en FAO-56 porque incluye la contribución positiva de la radiación y los controles de humedad y viento. Temperatura y radiación predominan; ea amortigua parcialmente el aumento y el viento no es relevante. Sin datos locales de tanque no es defendible declarar una paradoja del tanque; con la evidencia atmosférica disponible no se observa una compensación suficiente para contrarrestar el calentamiento.

## Referencias conceptuales

- Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop evapotranspiration: Guidelines for computing crop water requirements*. FAO Irrigation and Drainage Paper 56.
- Roderick, M. L., & Farquhar, G. D. (2002). The cause of decreased pan evaporation over the past 50 years. *Science*, 298, 1410--1411.
- McVicar, T. R., et al. (2012). Global review and synthesis of trends in observed terrestrial near-surface wind speeds. *Nature Geoscience*, 5, 756--760.
