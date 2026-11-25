# Punto 2 — Apartado 2.0: conceptos y ecuaciones

Este documento es el bloque conceptual que debe incorporarse a la metodología
del informe. Las ecuaciones se aplicarán después a la estación DWD 00020 y a la
microcuenca de Abtsgmünd, cuya delimitación preliminar es de 0.12315 km².

## 1. Probabilidad de excedencia, periodo de retorno y riesgo

Para una variable de máximos anuales `X`, sea `F(x) = Pr(X <= x)` su función de
distribución acumulada. La probabilidad anual de excedencia de `x_T` es:

`p = 1 - F(x_T)`

El periodo de retorno asociado es:

`T = 1/p`

`T` no significa que el evento ocurra exactamente cada `T` años. Si los años se
consideran independientes, el riesgo de exceder al menos una vez el diseño
durante `n` años es:

`R_n = 1 - (1 - 1/T)^n`

En el informe se deben distinguir siempre `p` (probabilidad anual), `T` (años)
y `R_n` (probabilidad acumulada durante la vida útil).

## 2. Profundidad, intensidad, duración e IDF

La profundidad de precipitación `P_d` es la lámina acumulada durante una
duración `d`, en milímetros. La intensidad media correspondiente es:

`i(d,T) = P_d(T) / d`

Si `d` está en horas, `i` queda en mm/h. Una curva IDF entrega `i(d,T)` para
varias duraciones y periodos de retorno. Para un resultado físicamente
coherente, la intensidad debe disminuir cuando aumenta `d` y las curvas de
distintos `T` no deben cruzarse.

La serie DWD está registrada cada 10 minutos. Las profundidades de 10 min, 30
min, 1 h, 3 h, 6 h, 12 h y 24 h se obtienen con ventanas móviles y luego se
analizan como máximos anuales.

## 3. Lluvia puntual y lluvia areal

El pluviómetro mide lluvia puntual. La lluvia media sobre la microcuenca puede
ser menor para duraciones cortas, por lo que puede usarse un factor de reducción
areal `FRA(A,d)`, con `0 < FRA <= 1`:

`P_areal = FRA(A,d) P_puntual`

En esta tarea se debe justificar si el área de 0.12315 km² y la duración de
diseño hacen necesario aplicar `FRA`. Si se usa, se debe reportar su fuente y
hacer sensibilidad con `FRA = 1` y con la alternativa adoptada.

## 4. Tiempo de concentración

El tiempo de concentración `tc` es el tiempo que tarda en llegar al outlet el
agua proveniente del punto hidráulicamente más lejano. Se expresará en minutos
u horas, pero nunca se mezclarán unidades dentro de una ecuación.

Se calculará con al menos tres fórmulas (por ejemplo, Kirpich, Kerby y SCS),
usando longitud y pendiente del cauce obtenidas de la delimitación DEM. La
elección final debe apoyarse en el rango de validez de cada fórmula y en la
fisonomía de la microcuenca, no solo en el promedio de los resultados.

## 5. Método racional

Para una cuenca pequeña, el caudal pico se estima como:

`Q_p = C i(tc,T) A / 3.6`

donde:

- `Q_p`: caudal pico en m³/s;
- `C`: coeficiente de escorrentía adimensional;
- `i(tc,T)`: intensidad IDF en mm/h para duración `tc` y retorno `T`;
- `A`: área en km²;
- `3.6`: conversión de mm·km²/h a m³/s.

Si hay varias coberturas, el coeficiente se pondera por área:

`C = sum(C_k A_k) / A`

El método supone lluvia espacialmente uniforme, duración efectiva igual a `tc`
y un `C` que no cambia con la humedad antecedente ni con la magnitud del evento.
Estas limitaciones deben aparecer en la discusión y en la sensibilidad `C ±20 %`.

## 6. Método racional de tiempo–área

Para obtener un hidrograma aproximado, el área contribuyente se hace crecer con
el tiempo de viaje. La expresión usada en la tarea es:

`Q(t) = C A / 3.6 * i_barra_tc(t)`

`i_barra_tc(t)` es la intensidad media de la lluvia durante los `tc` minutos
anteriores a `t`. Con una lluvia constante de duración igual o mayor que `tc`,
esta formulación recupera el pico del método racional.

## 7. Dimensionamiento con Manning

Para una tubería circular llena se usará la forma indicada en el PDF:

`Q = 0.312/n * D^(8/3) * S0^(1/2)`

Despejando el diámetro:

`D = [Q n / (0.312 S0^(1/2))]^(3/8)`

donde `n` es la rugosidad de Manning, `D` el diámetro en metros y `S0` la
pendiente construida en m/m. El diámetro calculado se redondeará hacia arriba al
diámetro comercial disponible y se comprobará la capacidad `Qc` de ese diámetro.

## 8. Riesgo efectivo y factor de seguridad

El riesgo nominal usa la distribución elegida y un único conjunto de
parámetros. El riesgo efectivo debe incorporar la incertidumbre de parámetros y
entradas mediante Monte Carlo: distribución/bootstrap, `C`, `tc`, `n` y
pendiente. Para cada iteración:

`i* = 3.6 Qc / (C A)`

La probabilidad anual de que la intensidad de duración `tc` exceda `i*` se
promedia entre iteraciones. También se reportará:

`FS = Qc / Qp`

y el riesgo acumulado durante la vida útil de la obra.

## 9. Tanque de detención

El balance de almacenamiento es:

`dS/dt = I(t) - O(h)`

Para una salida por orificio:

`O(h) = Cd Ao sqrt(2 g h)`

donde `Cd` es el coeficiente de descarga, `Ao` el área del orificio, `g` la
gravedad y `h` la carga hidráulica. Se necesita una relación `S(h)` del tanque.

El hietograma de diseño se construirá por bloques alternos y se repetirá con el
bloque máximo al inicio, centro y final. La duración crítica será la que produzca
el mayor volumen requerido, no necesariamente la de mayor intensidad puntual.

## 10. Convenciones que se adoptan

| Magnitud | Unidad de trabajo |
|---|---|
| Precipitación | mm |
| Intensidad | mm/h |
| Duración | min para ventanas cortas; h en IDF, siempre explícito |
| Área | km² en racional; m² al calcular almacenamiento |
| Caudal | m³/s |
| Longitud | m |
| Pendiente | m/m o %, indicando cuál se usa |
| Almacenamiento | m³ |
| Diámetro | m y diámetro comercial |

Convención de signo: la precipitación, el caudal de entrada y el almacenamiento
son positivos cuando aumentan el volumen disponible; el caudal de salida es
positivo cuando descarga el tanque. En el balance del tanque, `I(t)` y `O(h)`
deben estar en las mismas unidades de caudal (m³/s) y `S(h)` en m³. La
integración temporal usará un `dt` explícito y constante o documentará los pasos
variables.

## 11. Supuestos que deben revisarse en fases posteriores

1. La serie de 10 minutos representa el régimen de lluvia de la microcuenca.
2. Los máximos anuales son comparables después de definir el año hidrológico.
3. La microcuenca validada cumple el rango 0.1–5 km² y drena a una estructura
   real.
4. El método racional es aplicable al tamaño y uso del suelo de la cuenca.
5. La independencia anual y la estacionariedad son hipótesis de trabajo, no
   hechos garantizados.
6. El valor de `C`, `tc`, Manning, `FRA` y la geometría del tanque tienen
   incertidumbre y deben entrar en sensibilidad o Monte Carlo.

## 12. Referencias metodológicas que deben aparecer en el informe

Las ecuaciones no deben quedar sin fuente. La metodología debe citar, como
mínimo, el PDF de la tarea y las referencias que este recomienda: Chow et al.
para método racional, Manning y riesgo; Weiss para máximos de intervalos fijos;
Svensson y Jones para reducción areal; y Kuiry y Sen para tránsito de embalses.
La lista bibliográfica final debe contener las referencias completas y cada cita
debe corresponder a una afirmación concreta.

## Criterio de cierre del apartado 2.0

El apartado queda cerrado cuando el informe contiene estas definiciones,
ecuaciones, unidades y supuestos, y cada símbolo se usa de forma consistente en
2.1–2.4. La siguiente fase es 2.1: definir el año hidrológico y cerrar la
justificación espacial de la microcuenca.
