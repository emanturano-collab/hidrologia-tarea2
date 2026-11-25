# 1.1.c — Métodos de otras familias (versión preliminar)

## Alcance reproducible
Se procesaron **20 celdas ERA5-Land** por separado y después se ponderaron con los pesos de la Tarea 1, renormalizados sobre el dominio disponible. La cobertura es 90.1264%; el 9.8736 % restante sigue pendiente. El periodo común comparable es enero de 1981–diciembre de 2022 (504 meses): Thornthwaite exige un índice térmico anual completo; por ello se excluyó 2023, que está incompleto, sin rellenar datos. Todas las tablas están en mm/mes salvo indicación contraria.

## Métodos, ecuaciones y uso
* **Thornthwaite (1948, temperatura):** `PET=16(10T/I)^a (N/12)(d/30)` mm/mes, con `I=sum((T/5)^1.514)` (solo T>0) y `a=6.75e-7 I³−7.71e-5 I²+1.792e-2 I+0.49239`. T es °C, N horas de luz y d días. Se implementó en mensual y años completos; T≤0 contribuye cero. Fue formulado para estimar evapotranspiración potencial a partir de temperatura y latitud; omite radiación observada, humedad y viento.
* **Hargreaves–Samani (1985, temperatura+Ra):** `ET0=0.0023(Tmean+17.8)sqrt(Tmax−Tmin) Ra`, con `Ra` en mm d⁻¹ equivalentes (`Ra_MJ/2.45`). T en °C. Simplifica radiación, humedad y viento mediante el rango térmico. Aplicado como contraste de bajo requerimiento, no calibrado para Racarumi.
* **Priestley–Taylor (1972, radiación):** `ET=1.26 Δ/(Δ+γ)(Rn−G)/λ`; Δ y γ en kPa °C⁻¹, Rn/G MJ m⁻² d⁻¹ y λ MJ kg⁻¹. Representa una superficie húmeda con disponibilidad de energía; omite explícitamente el término aerodinámico. Se usó α=1.26, sin calibración.
* **Meyer (1915, transferencia de masa):** `E=0.36(e_w−e_a)(1+u_9/16)`, E mm d⁻¹, presiones en mm Hg y u en km h⁻¹ aproximadamente a 9 m. Ante la ausencia de unas notas del curso que fijen una constante Dalton, se aplicó Meyer —permitido por la guía— con una formulación publicada y sin calibrarla. Se usó `e_w=es(Taire media)` por ausencia de temperatura de agua y u10 como aproximación a u9. Es evaporación de agua libre y no ETo.
* **Makkink (1957, radiación solar):** `PET=0.65 Δ Rs/[λ(Δ+γ)]`, con Rs MJ m⁻² d⁻¹. Se aplicó mediante `pyet.makkink` v1.5.0, con λ dependiente de T. Es una formulación calibrada para pasto en los Países Bajos; omite humedad y viento explícitos.
* **Rohwer (1931, transferencia de masa):** `E=0.771(1.465−0.000732P_a)(0.44+0.0733u_0)(e_w−e_a)`, E mm d⁻¹, P/e en mm Hg y u0 en km h⁻¹ a 0.6 m. `u0=u10(0.6/10)^(1/7)` y `e_w=es(Taire media)` son aproximaciones declaradas por falta de viento bajo y temperatura de agua. Es evaporación de agua libre, no ETo; se usa solo como contraste físico experimental.

## Referencias metodológicas
Thornthwaite, C.W. (1948), *An approach toward a rational classification of climate*, Geographical Review 38, 55–94. Hargreaves, G.H. & Samani, Z.A. (1985), *Reference crop evapotranspiration from temperature*, Applied Engineering in Agriculture 1, 96–99. Priestley, C.H.B. & Taylor, R.J. (1972), *On the assessment of surface heat flux and evaporation using large-scale parameters*, Monthly Weather Review 100, 81–92. Meyer, A.F. (1915), *Computing runoff from rainfall and other physical data*. Makkink, G.F. (1957), *Testing the Penman formula by means of lysimeters*, Journal of the Institution of Water Engineers 11, 277–288. Rohwer, C. (1931), *Evaporation from free water surfaces*, U.S. Department of Agriculture Technical Bulletin 271. Allen et al. (1998), FAO-56.

## Control manual independiente
La tabla `1_1c_comprobacion_manual.csv` conserva todas las entradas y salidas para un día/celda y para el primer mes completo de Thornthwaite. El anexo `verificacion_manual_con_sustitucion_1_1c.md` muestra la sustitución numérica. `1_1c_control_pyET.csv` registra la verificación de Hargreaves contra pyet (una celda con índice temporal único); Priestley–Taylor y Makkink se ejecutaron directamente con pyet v1.5.0.

## Resultados y respuestas a la guía
En la serie mensual común, el menor MAE fue **Makkink** (5.047 mm/mes); esto es un ranking por MAE, no un ganador universal. El mayor MAE fue **Meyer** (58.595 mm/mes). La desviación mensual de mayor magnitud fue Meyer en el mes 3: -69.438 mm/mes (alternativo−FAO-56).

**Pregunta 1.** Por MAE y RMSE mensuales, Makkink es el más cercano (MAE 5.047; RMSE 5.513 mm/mes), seguido por Hargreaves–Samani (MAE 6.068). También tiene la mayor correlación de Pearson (0.977). No es un ganador universal: Priestley–Taylor mantiene alta correlación (0.959) pero sobrestima 20.151 mm/mes. Los resultados anuales y cada mes calendario están en sus CSV respectivos.

Primer armónico de la climatología (diferencia = alternativo − FAO-56):

| method            |   amplitude_difference_alt_minus_fao_mm_month |   phase_difference_alt_minus_fao_months |   climatological_maximum_month |
|:------------------|----------------------------------------------:|----------------------------------------:|-------------------------------:|
| Thornthwaite      |                                        -9.323 |                                   0.124 |                             12 |
| Hargreaves-Samani |                                        -0.740 |                                   0.661 |                             10 |
| Priestley-Taylor  |                                         2.340 |                                   0.584 |                             10 |
| Meyer             |                                         3.508 |                                  -2.037 |                              8 |
| Makkink           |                                        -0.424 |                                  -0.385 |                             10 |
| Rohwer            |                                         5.640 |                                  -2.070 |                              8 |

**Pregunta 2.** El comportamiento esperado se interpreta como hipótesis: los métodos radiativos deberían acercarse cuando Rn/Rs domina, mientras los métodos de masa divergen al representar agua libre y requerir temperatura de agua/viento a otras alturas. Los térmicos pueden compensar errores mediante el rango térmico. No se infiere aquí un forzante dominante: esto se contrasta en 1.1.d.

**Pregunta 3.** Los mayores alejamientos por método y su dirección son:

| method            |   month |   bias_alt_minus_fao_mm |
|:------------------|--------:|------------------------:|
| Hargreaves-Samani |       8 |                  -8.943 |
| Makkink           |       5 |                   7.778 |
| Meyer             |       3 |                 -69.438 |
| Priestley-Taylor  |       1 |                  23.379 |
| Rohwer            |       3 |                 -66.794 |
| Thornthwaite      |      11 |                 -49.671 |

Meyer y Rohwer son los más alejados: subestiman porque representan una superficie de agua libre con proxies de temperatura superficial y altura de viento, no una referencia de pasto. Frente a 1.1.b, estos son métodos ejecutados sobre el mismo dominio de Racarumi. Como contexto, PISCOeo_pm frente a FAO-56 tuvo MAE 7.970 mm/mes (432 meses) y TerraClimate frente a FAO-56, 4.017 mm/mes (511 meses); no se usa Chiclayo como umbral de incertidumbre de cuenca.

## Limitaciones decisivas
Meyer y Rohwer dependen de temperatura de agua y alturas de viento que ERA5-Land no aporta en esta serie; por ello son escenarios de evaporación de agua libre con proxies, no estimaciones de ETo. La referencia FAO-56 y todos estos resultados siguen siendo preliminares por la cobertura espacial incompleta.

## Nota de la revisión final (24/11/2026)

La fórmula de Makkink aplicada (`pyet.makkink`, k = 0,65, sin constante) es la variante de de Bruin (1987), no la forma original de Makkink (1957), `0,61 Δ/(Δ+γ) Rs/λ − 0,12` mm/d. La forma original se calcula como sensibilidad en `codigo/punto1/1_1_demanda_atmosferica/1_1_d_explicacion_fisica/calibrar_hargreaves_1_1d.py`: sesgo de −5 % frente a +5 % de la variante. El mismo script calibra Hargreaves contra FAO-56, como pide el árbol de decisión de la sección 7 de las notas del curso.
