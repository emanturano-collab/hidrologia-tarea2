# Fuentes y decisiones - apartado 1.1.a

## Insumos

- ERA5-Land horario en ocho puntos, leído directamente desde los ZIP originales.
- Periodo solicitado y verificado cuando el punto está completo: 1981-01-01 00:00 a 2023-08-31 23:00 UTC.
- Delimitación y elevación SRTM reutilizadas de la Tarea 1. La elevación por punto es la media SRTM de la porción de celda ERA5-Land dentro de la cuenca.
- La Tarea 1 identificó 33 celdas ERA5-Land que intersectan la cuenca. La elevación media ponderada SRTM es 2348.98 m, frente a 2367.17 m en la orografía nativa ERA5-Land (diferencia 18.19 m).

## Decisiones de cálculo

- La agregación diaria se hace en `UTC-05:00` fijo (hora estándar de Perú) y solo conserva días locales con 24 horas. Se evita una zona horaria histórica con cambios de horario que produciría artificialmente días de 23 o 25 horas.
- `t2m` y `d2m`: K a °C restando 273.15; `sp`: Pa a kPa dividiendo entre 1000.
- La magnitud del viento se calcula cada hora como `sqrt(u10^2 + v10^2)` y luego se promedia. Se transforma de 10 m a 2 m con la ecuación 47 de FAO-56.
- `ssrd` es una acumulación horaria en J m-2; para `Rs` diario se suman las 24 horas y se divide entre 1,000,000 para obtener MJ m-2 d-1.
- `Rn` es la radiación neta del pasto de referencia: Rns usa albedo 0.23 y Rnl usa la ecuación FAO-56. No se usa como Rn la radiación neta de la superficie real de ERA5-Land.
- En escala diaria se usa G = 0. Para el cálculo directo mensual se usa G_i = 0.07(T siguiente - T previa); enero de 1981 y agosto de 2023 quedan sin cálculo directo mensual por no tener meses vecinos a ambos lados.

## Limitación espacial

No se calcula una ETo promedio de cuenca: las ocho ubicaciones seleccionadas equivalen a solo 0.326 de la ponderación de intersección de las 33 celdas de la Tarea 1. Además, P5 está incompleto. Los productos contienen únicamente resultados por punto validado.

## Estado de los puntos

- Validados para cálculo: P1, P2, P3, P4, P6, P7, P8.
- Bloqueados: [{'point': 'P5', 'issues': 'Variables obligatorias ausentes: ssrd | El complemento P5 contiene strd (radiación térmica descendente), no ssrd.'}].
