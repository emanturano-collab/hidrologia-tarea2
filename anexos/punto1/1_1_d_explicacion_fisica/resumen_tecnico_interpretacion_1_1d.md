# 1.1.d - Explicar las diferencias (preliminar)

## Alcance y criterio espacial
Se usan 20 celdas ERA5-Land y pesos de intersección de Tarea 1 renormalizados sobre el dominio disponible (90.1264%). Cada ecuación se aplicó por celda antes de ponderar. El periodo común es enero de 1981 a diciembre de 2022 (504 meses); Chiclayo no participa.

## Descomposición FAO-56
`ETo = R + A`, donde `R=0.408 Δ(Rn-G)/[Δ+γ(1+0.34u2)]` y `A=γ[900/(T+273)]u2(es-ea)/[Δ+γ(1+0.34u2)]`. Sus fracciones mensuales son sum(R)/sum(ETo) y sum(A)/sum(ETo), por lo que son relaciones de contribuciones acumuladas y no promedios de porcentajes diarios.

`α*=ETo/Eeq`, con `Eeq=Δ/(Δ+γ)(Rn-G)/λ`, usa λ=2.45 MJ kg-1 y queda adimensional. Se excluyen Eeq<=0; el conteo queda en control de calidad. α=1.26 de Priestley-Taylor se muestra solo como referencia. FAO-56 incluye resistencia superficial del pasto de 70 s m-1; por ello α* no se interpreta como diagnóstico único de advección. Valores altos son compatibles con aire seco/advección, no los prueban.

## Sensibilidad
Los siete escenarios cambian una sola entrada a la vez. Al cambiar temperatura se recalculan es, Δ, VPD y Rnl; en HR constante, ea se escala por es nuevo/es original. En ea+10 %, ea se limita a es para evitar sobresaturación y se informa su frecuencia. Thornthwaite recalcula I y a anualmente. Meyer/Rohwer siguen etiquetados como agua libre.

El mayor cambio absoluto anual de FAO-56 fue **Rs_minus10pct**: -84.695 mm/año (-7.186 %). Esto no identifica un forzante universal: los tamaños y unidades de las perturbaciones no son comparables entre sí.

## Dispersión de 1.1.b
PISCOeo_pm y TerraClimate se presentan como distribuciones empíricas de diferencias mensuales respecto a FAO-56, por mes calendario (media, desviación, percentiles 5--95); no son intervalos de confianza. Chiclayo se excluye de este diagnóstico espacial.

## Explicación de 1.1.c
Makkink concuerda mejor en los productos reales de 1.1.c porque usa Rs y el balance Δ/(Δ+γ), compartiendo parte de la física radiativa con FAO-56, aunque puede haber compensación de errores. Hargreaves usa Ra y rango térmico: reproduce estacionalidad pero omite humedad/viento. Priestley-Taylor usa Rn, pero su α=1.26 y ausencia de resistencia aerodinámica/superficial explícita explica su sesgo positivo. Thornthwaite depende solo de T y duración del día; su débil amplitud y subestimación no capturan variación de radiación/humedad/viento. Meyer y Rohwer son agua libre y dependen de proxies de temperatura superficial y altura de viento; no son ETo de pasto.

No se hallaron en el proyecto las notas del curso ni el árbol de decisión de su sección 7. Para justificar formalmente la elección de un método simple con solo temperatura se requiere proporcionar esas notas o una captura de esa sección. Sin atribuir un árbol inexistente al profesor, Thornthwaite es el único método de esta implementación que usa únicamente temperatura y duración del día, con las limitaciones observadas.

Milly y Dunne (2016) advierten que una formulación solo térmica puede reproducir el ciclo anual y exagerar sensibilidad al calentamiento; los escenarios con Thornthwaite quedan preparados para contrastar este punto en 1.4.

## Verificación de unidades
146 W m-2 × 3600 s h-1 / (2.45e6 J kg-1) = 0.214531 kg m-2 h-1 = 0.214531 mm h-1, o 5.148735 mm d-1. El valor citado de 3.52 mm h-1 es 16.4 veces mayor: corresponde aproximadamente a 3.52 mm/d. Inversamente 1 mm/d equivale a 28.356 W m-2 sostenidos, aproximadamente 28 W m-2.
