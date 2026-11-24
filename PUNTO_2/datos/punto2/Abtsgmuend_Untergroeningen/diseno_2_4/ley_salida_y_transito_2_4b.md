# Ley de salida y tránsito del tanque (2.4B)

El tanque rectangular tiene planta 24 × 22 m (área 528 m²), profundidad útil 2.0 m y borde libre 0.5 m. Se usa piscina nivelada con

`dS/dt = I(t) - O(h)`

`S(h) = 528 h` y salida por orificio `O(h) = Cd Ao sqrt(2 g h)`, con `Cd=0.65`, diámetro del orificio 0.30 m y `Ao=πd²/4=0.07069 m²`. La integración usa pasos de 10 minutos, condición inicial S=0 y `h=S/528`.

Se evaluaron duraciones de 30, 60 y 90 minutos y el pico al inicio, centro y final. El caso crítico es 60 min con pico final: 1014.75 m³, 1.92 m, margen 41.25 m³. La salida a h=2 m es 0.288 m³/s.
