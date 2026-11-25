# 1.2.5. Torres de flujo: disponibilidad y decisión metodológica

Fecha de consulta de las fuentes: **22 de noviembre de 2026**.

## Alcance

Se evaluó la disponibilidad de torres de covarianza de remolinos que pudieran servir como referencia independiente para la cuenca Racarumi (`PE_200907`) y para la climatología mensual obtenida con GLEAM4.3a y MOD16A2GF. La delimitación de referencia fue el archivo original de la Tarea 1, `datos/punto1/PE_200907_catchment_T1_original.gpkg`.

El centroide areal usado para calcular las distancias es 6,650574° S y 78,971274° O. El área de la cuenca es aproximadamente 2363,30 km². Las distancias se calcularon geodésicamente sobre WGS84 desde ese centroide hasta las coordenadas publicadas de cada torre.

Este trabajo fue un diagnóstico documental. **No se descargaron series de torres**, no se procesaron flujos y no se modificaron los resultados anteriores de GLEAM4.3a, MOD16A2GF ni del balance hídrico.

## Criterio para clasificar la evidencia

Se conservaron tres categorías distintas:

1. **Datos públicos:** existe un producto descargable identificado en un catálogo oficial.
2. **Datos bajo solicitud:** la publicación indica que los datos pueden pedirse a los autores, pero no ofrece descarga pública directa.
3. **Variables documentadas en publicaciones:** el artículo describe la medición o el uso de LE, H, Rn o G. Esto no demuestra que esas variables estén presentes, completas ni continuas dentro de un paquete público no inspeccionado.

Cuando una ficha solo declara flujos de `H2O` o muestra un instrumento, no se asumió automáticamente que existiera una serie utilizable de LE, H, Rn o G.

## Síntesis de las estaciones examinadas

| Código | Estación | Distancia (km) | Elevación (m) | Periodo documentado | Acceso | Estado de LE, H, Rn y G | Limitación principal |
|---|---|---:|---:|---|---|---|---|
| PE-BRE | El Breo | 206,1 | 755 | 2023–presente | Sin producto público | No verificadas en archivos | Bosque amazónico Af, fuera de la cuenca, menor elevación y sin coincidencia temporal suficiente. |
| RBSF | Reserva Biológica San Francisco | 296,2 | 1984 | ene. 2020–dic. 2022 | Bajo solicitud | Las cuatro variables están documentadas en la publicación | Bosque montano húmedo de ladera en Ecuador; solo tres años y terreno complejo. |
| EC-APr | Zhurucay | 398,0 | 3780 | mar. 2017–feb. 2018; otro estudio usa may. 2017–abr. 2018 | No se confirmó producto público de red | Las cuatro variables están documentadas en publicaciones | Páramo mucho más alto, frío y húmedo; serie cercana a un año. |
| PE-PAN | Panguana | 553,4 | 220 | 2023–presente | Sin producto público | No verificadas en archivos | Bosque amazónico Af, baja elevación, distante e inicio al final del periodo. |
| PE-QFR | Quistococha | 699,7 | 104 | Producto 2018–2022; años completos publicados 2018, 2019 y 2022 | BASE y FLUXNET públicos | Las cuatro variables están documentadas; el paquete no fue auditado por variable | Aguajal amazónico sobre turba, muy húmedo, bajo y distante; periodo corto y discontinuo. |
| PE-IGP | Huancayo, sitio AmeriFlux actual | 718,6 | 3336 | 2025–presente | Sin producto público | No verificadas en archivos | Inició después del periodo de comparación y está en los Andes centrales. |
| — | Huancayo, campaña histórica | 718,5 | 3330 | jul. 2016–jun. 2017 | Resultados publicados; no se localizó serie cruda pública normalizada | LE, H y Rn documentadas; G derivado de temperatura y humedad del suelo | Solo un año y región diferente. No debe confundirse con el sitio AmeriFlux iniciado en 2025. |
| PE-AMG | Los Amigos | 1172,2 | 290 | 2021–presente | Sin producto público | No verificadas en archivos | Bosque amazónico de baja elevación y muy distante. |
| PE-TNR | Tambopata | 1263,3 | 214 | 2015–presente | Sin producto público | Rn tiene instrumentación visible, pero la serie no se verificó; las demás no se verificaron | Muy distante, bosque amazónico de baja elevación y sin producto público. |

No se identificó una torre de covarianza de remolinos dentro de Racarumi ni en la cuenca Chancay–Lambayeque que reuniera cercanía, representatividad hidroclimática, datos públicos y un periodo compatible con los 21 años hidrológicos.

La tabla completa, con coordenadas, coberturas, clima, estado separado de LE, H, Rn y G y el vínculo entre cada afirmación y su fuente, se conserva en `productos/punto1/punto_1_2_5_disponibilidad_torres.xlsx`.

## Por qué las estaciones encontradas no constituyen una validación directa

### PE-QFR: disponibilidad no equivale a representatividad

PE-QFR es la única estación peruana localizada en el catálogo consultado con productos AmeriFlux BASE y FLUXNET públicos para 2018–2022 ([ficha AmeriFlux](https://ameriflux.lbl.gov/sites/siteinfo/PE-QFR), [DOI BASE](https://doi.org/10.17190/AMF/1671889), [DOI FLUXNET-1F](https://doi.org/10.17190/AMF/1832157)). Sin embargo, la torre está a unos 699,7 km del centroide de Racarumi, a 104 m s. n. m., dentro de un aguajal amazónico sobre turba y bajo clima Af. La publicación del sitio documenta LE, H, Rn y G, pero describe condiciones hidrológicas y de vegetación muy diferentes de las de Racarumi ([Griffis et al., 2020](https://doi.org/10.1016/j.agrformet.2020.108167)).

Además, una publicación posterior identifica como años completos 2018, 2019 y 2022 y atribuye la interrupción de dos años a rayos y a dificultades de reparación durante la pandemia ([Wood et al., 2025](https://doi.org/10.1029/2025GL114642)). Por ello, una climatología de PE-QFR tendría poca extensión temporal y no sería equivalente al periodo de los 21 años hidrológicos de Racarumi. Una comparación podría ser ilustrativa de otro ecosistema, pero no una validación local.

### El Breo y las otras estaciones amazónicas

PE-BRE es la estación registrada más cercana, aproximadamente a 206,1 km, pero está en un bosque latifoliado siempreverde de clima Af a 755 m y su ficha indica mediciones desde 2023 sin años públicos ([AmeriFlux PE-BRE](https://ameriflux.lbl.gov/sites/siteinfo/PE-BRE)). PE-AMG, PE-PAN y PE-TNR presentan el mismo problema general: bosques amazónicos de baja elevación, distancias mayores y ausencia de productos públicos en el catálogo consultado ([búsqueda oficial AmeriFlux](https://ameriflux.lbl.gov/sites/site-search/)). La cercanía relativa de PE-BRE no compensa las diferencias de clima, cobertura, elevación y periodo.

### Huancayo, RBSF y Zhurucay

Estas estaciones aportan antecedentes andinos, pero tampoco satisfacen conjuntamente los criterios:

- La ficha actual PE-IGP de Huancayo registra el sitio desde 2025 sin datos públicos ([AmeriFlux PE-IGP](https://ameriflux.lbl.gov/sites/siteinfo/PE-IGP)). La campaña histórica de julio de 2016 a junio de 2017 sí documenta LE, H, balance radiativo y G derivado, pero solo cubre un año y no se localizó un archivo público normalizado de la serie cruda ([Callañaupa et al., 2021](https://doi.org/10.1016/j.atmosres.2021.105760)).
- RBSF documenta LE, H, componentes radiativos y G entre enero de 2020 y diciembre de 2022, pero los datos están disponibles bajo solicitud. Es un bosque montano húmedo en ladera a 1984 m, con efectos de terreno complejo ([Murkute et al., 2024](https://doi.org/10.3390/f15101828)).
- EC-APr, Zhurucay, representa un páramo húmedo alrededor de 3780 m. Los artículos documentan mediciones de LE y H y la instrumentación del balance energético, pero las series analizadas son cercanas a un año y no se confirmó un producto público descargable de FLUXNET ([Córdova et al., 2020](https://doi.org/10.3390/atmos11020213); [Ochoa-Sánchez et al., 2019](https://doi.org/10.3389/feart.2019.00055)).

## Incompatibilidad de escala

GLEAM4.3a y MOD16A2GF fueron promediados espacialmente sobre toda la cuenca Racarumi, de aproximadamente 2363 km². Una torre mide intercambios turbulentos de un área fuente o *footprint* alrededor del instrumento. Este footprint cambia con la dirección del viento, la estabilidad atmosférica, la altura de medición, la rugosidad y la heterogeneidad de la superficie; no representa automáticamente una cuenca completa ([Chu et al., 2026](https://doi.org/10.1111/gcb.70887)).

La comparación torre–producto solo sería defendible si se trabajara a la escala del footprint o de los píxeles que lo contienen, con coincidencia temporal, cobertura homogénea y controles de calidad. Comparar directamente un flujo puntual de otro ecosistema con el promedio de una cuenca andina heterogénea introduciría diferencias de escala que no pueden atribuirse al error de GLEAM o MOD16.

## Cierre del balance de energía

La covarianza de remolinos tampoco garantiza por sí sola el cierre perfecto de

\[
R_n-G-S=H+LE,
\]

donde `S` reúne términos de almacenamiento que pueden ser relevantes. El estudio clásico de 22 sitios FLUXNET encontró un desequilibrio medio del orden de 20 % y documentó problemas asociados con almacenamiento, mezcla débil y otros términos no medidos ([Wilson et al., 2002](https://doi.org/10.1016/S0168-1923(02)00109-0)). En bosques y terreno complejo también deben considerarse almacenamiento en la biomasa y el aire del dosel, advección y circulaciones de ladera.

Por tanto, aun si se utilizara una torre comparable, sería necesario revisar como mínimo la cobertura temporal, las banderas de calidad, el tratamiento de datos faltantes, el *footprint*, los términos de almacenamiento y una métrica de cierre como

\[
EBR=\frac{H+LE}{R_n-G-S}.
\]

No sería correcto ajustar automáticamente LE para forzar el cierre sin declarar el método y su efecto.

## Decisión metodológica para el numeral 1.2.5

**No se realizará una validación cuantitativa directa de GLEAM4.3a o MOD16A2GF con las torres identificadas.** Ninguna reúne simultáneamente:

- ubicación dentro de Racarumi o proximidad hidroclimáticamente defendible;
- cobertura y régimen climático representativos;
- datos públicos de LE con controles asociados de H, Rn y G;
- periodo suficiente y compatible con la comparación hidrológica;
- escala espacial adecuada para representar el promedio de la cuenca.

PE-QFR no se usará como sustituto de una observación local solo porque sus datos sean públicos. RBSF, Zhurucay y Huancayo pueden citarse como antecedentes metodológicos andinos, pero no como validaciones directas de Racarumi.

La ausencia de una torre adecuada **no demuestra que GLEAM4.3a o MOD16A2GF sean precisos ni imprecisos**. Únicamente indica que, con la evidencia disponible y los criterios adoptados, no es posible efectuar una validación local independiente mediante covarianza de remolinos. Esta limitación debe declararse en el informe final sin reemplazarla por una comparación cuantitativa con una estación no representativa.

## Trazabilidad

El registro tabular de fuentes consigna, para cada ficha o publicación, la institución, el enlace, la información consultada, el alcance real de la comprobación y la fecha de consulta. En particular, se dejó explícito que:

- no se descargaron ni examinaron los archivos internos de PE-QFR;
- no se afirmó la presencia de variables en productos que no se inspeccionaron;
- la instrumentación mencionada en una ficha o publicación no se trató como prueba de una serie pública continua;
- la campaña histórica de Huancayo no se confundió con el sitio AmeriFlux PE-IGP iniciado en 2025;
- no se encontró un producto público FLUXNET de EC-APr durante la búsqueda, lo que no equivale a afirmar que los datos no existan bajo custodia institucional.
