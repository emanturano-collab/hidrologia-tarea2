# Discusión final de los apartados 2.2 y 2.3

## 2.2 Extremos y distribuciones

### Selección del modelo

Se compararon Gumbel, GEV y Log-Pearson III mediante momentos, L-momentos y
máxima verosimilitud. La selección se realizó con las pruebas Kolmogorov–Smirnov,
Cramér–von Mises, gráficos de probabilidad y razones de L-momentos.

La combinación recomendada es **GEV por máxima verosimilitud**, con promedio de
p-valores KS + CvM de 1.7565, superior a las demás combinaciones evaluadas.
Esto no significa que GEV sea la verdad física: significa que fue el modelo con
mejor desempeño estadístico conjunto en esta muestra.

### Incertidumbre

Los cuantiles se acompañan con bootstrap GEV-MLE. La incertidumbre es moderada
para duraciones cortas y aumenta considerablemente hacia 6–24 h y periodos de
retorno altos. En particular, algunos intervalos bootstrap de 12 h presentan
valores extremos y anchuras no realistas; esto evidencia inestabilidad de la
extrapolación y no debe interpretarse como una predicción precisa.

Por lo tanto, para el diseño se usa la curva GEV-MLE como estimación central,
pero se reporta el intervalo bootstrap y se advierte que los cuantiles largos
son sensibles al modelo y al tamaño de muestra.

### Estacionariedad

Las pruebas de Kendall muestran p-valores entre 0.26 y 0.92 para las
duraciones analizadas. No se rechaza la hipótesis de ausencia de tendencia al
5 %. Las pendientes de Sen tienen intervalos que incluyen cero. La conclusión
correcta es **no se detectó tendencia estadísticamente significativa**, no que
el clima sea necesariamente estacionario en el futuro.

## 2.3 Curvas IDF

### Construcción y elección

La IDF se construyó a partir de los máximos anuales hidrológicos y la GEV-MLE.
Las intensidades aumentan al disminuir la duración y al aumentar el periodo de
retorno, como exige la coherencia hidrológica. Las curvas se guardan en
`idf_gev_mle.csv`, `idf_powerlaw_curves.csv` e `idf_gev_mle.png`.

### Comparación con KOSTRA-DWD-2020

La comparación se realizó para 10 min, 1 h, 6 h y 24 h. Los cocientes
`IDF_estimada/KOSTRA` son menores que 1 para T=2 en todas las duraciones, pero
superan 1 en varios escenarios de mayor retorno. Los contrastes más fuertes
aparecen en 1 h y 6 h para T=50–100; por ejemplo, el cociente es 2.03 para 1 h
y T=100, y 2.08 para 6 h y T=100.

Esto indica que la estimación local es más severa que KOSTRA en la cola de
retorno alto. No se debe promediar ambas curvas sin justificación: se conserva
la IDF local como resultado principal y KOSTRA como referencia externa de
plausibilidad y sensibilidad.

### Evento reciente

El máximo de 1 h del año hidrológico 2021 fue 48.27 mm y su periodo de retorno
estimado con GEV-MLE es aproximadamente **17.4 años**. Es un evento importante,
pero no equivale por sí solo a una tendencia climática ni reemplaza el análisis
de máximos anuales.

## Dictamen para abrir 2.5

Los apartados 2.2 y 2.3 quedan cerrados metodológicamente con estas
limitaciones explícitas: incertidumbre alta en extrapolaciones largas,
comparación conservadora frente a KOSTRA y ausencia de tendencia significativa
en la muestra. Conjuntamente con el cierre documentado de 2.4, ya se puede
iniciar el apartado **2.5 (bonificaciones)**.
