# Auditoría final del apartado 1.4

## Datos y reproducibilidad

La auditoría utilizó los 504 meses completos entre enero de 1981 y diciembre de 2022. La ETo FAO-56 mensual se agregó desde la serie diaria; todos los meses tienen el número esperado de días. Thornthwaite se tomó de la tabla maestra mensual ya calculada. El script `run_1_4_1_auditoria.py` reproduce las verificaciones adicionales sin modificar las fuentes.

## 1.4.1: estacionalidad, dependencia y extremos

Se aplicó Mann--Kendall y Sen a cada mes calendario. Los doce p mensuales de cada método se corrigieron mediante Benjamini--Hochberg. Cuando la autocorrelación lag 1 de la serie detrendida superó el límite aproximado de 1.96/sqrt(n), se aplicó trend-free prewhitening (TFPW) antes de evaluar la significancia; la pendiente de Sen se conserva en las unidades originales.

Para FAO-56, septiembre fue el único mes significativo después de FDR y TFPW (Sen = +0.172 mm/mes por año; q = 0.0269). Para Thornthwaite, julio, septiembre, octubre y noviembre fueron significativos después de FDR, con pendientes de +0.050, +0.042, +0.065 y +0.073 mm/mes por año, respectivamente. La prueba MK estacional conjunta es positiva para ambos métodos: FAO-56 Sen estacional = +0.099 mm/mes por año (p = 3.03e-7; p TFPW = 1.39e-7) y Thornthwaite = +0.042 mm/mes por año (p = 9.78e-9; p TFPW = 9.60e-9).

En las series anuales, la autocorrelación de los residuos de tendencia es 0.238 para FAO-56 y 0.120 para Thornthwaite, ambas por debajo del límite de diagnóstico 0.302 para n = 42. Como contraste, OLS con errores Newey--West de rezago 3 conserva significancia para ambos métodos (p = 7.91e-7 y 2.19e-9, respectivamente). La corrección no cambia el signo ni la conclusión de significancia.

Se evaluaron 49 escenarios por método: registro completo, seis recortes predefinidos de inicio o final y 42 exclusiones leave-one-out. En todos los escenarios se mantuvo el signo positivo, MK significativo y OLS HAC significativo. Las pendientes Sen variaron entre +1.057 y +1.411 mm/año por año para FAO-56, y entre +0.524 y +0.673 mm/año por año para Thornthwaite. Las observaciones con Cook's D superior a 4/n se retuvieron en la serie fuente y fueron usadas únicamente como diagnóstico: 1994 para FAO-56; 1983 y 1985 para Thornthwaite. Ninguna exclusión individual invirtió el signo ni eliminó la significancia.

## 1.4.2: atribución

Los productos existentes son consistentes con la tabla de atribución: temperatura (+0.760 mm/año por año) y radiación solar (+0.569) dominan la tendencia; ea aporta -0.127, u2 +0.008. La suma (+1.210) reproduce razonablemente la pendiente OLS directa (+1.163), con residuo -0.047 mm/año por año. Es una descomposición local de primer orden, no una demostración causal completa.

## 1.4.3: paradoja del tanque

FAO-56 y Thornthwaite aumentan durante 1981--2022. No hay registros locales de evaporación de tanque; por tanto, una paradoja del tanque no puede ser evaluada empíricamente. La evidencia disponible sostiene aumento de demanda evaporativa, con compensación parcial por ea insuficiente frente a temperatura y radiación.

## Dictamen

Los requisitos obligatorios de 1.4.1, 1.4.2 y 1.4.3 están cubiertos con las limitaciones declaradas. La bonificación Budyko no forma parte de este dictamen.
