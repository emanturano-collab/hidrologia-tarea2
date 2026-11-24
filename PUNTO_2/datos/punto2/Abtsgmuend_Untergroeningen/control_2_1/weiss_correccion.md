# Corrección de Weiss (1964)

La estación DWD 00020 registra acumulados en intervalos fijos de 10 minutos
(00, 10, 20, …, 50). El procesamiento de extremos usa ventanas móviles de 10
minutos, 30 minutos, 1, 3, 6, 12 y 24 horas. Por tanto, los máximos de la serie
principal no son máximos de una única ventana fija de reloj y no se aplica una
segunda corrección de Weiss a `ams_hydrological_oct_sep.csv`.

La decisión final es: **ventanas móviles + factor Weiss adicional igual a 1.0
(no aplicado)**, para evitar doble corrección. Si se analizara una serie de
máximos estrictamente fija, la corrección sería `1/(1 - 1/(8n))`, donde `n` es
el número de intervalos de la duración.
