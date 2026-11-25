# Resultados técnicos — ETo FAO-56 preliminar (90.13 %)

**Alcance.** Esta estimación usa 20 de las 33 celdas ERA5-Land y cubre 90.1264% del peso espacial. El 9.8736% restante sigue sin datos horarios, por lo que no es la ETo definitiva de Racarumi.

## Respuestas de 1.1.a

1. **Temperatura.** T2m se convirtió de K a °C y se promedió espacialmente por hora antes de obtener Tmin, Tmax y Tmedia diarios. El cálculo usa el promedio de e°(Tmax) y e°(Tmin) para es.
2. **Humedad.** La presión real de vapor se calculó horario a horario como e°(Td), con Td de ERA5-Land, y luego se promedió a día.
3. **Viento.** La magnitud sqrt(u10²+v10²) se formó por celda y hora antes de la ponderación espacial; la media diaria se transformó a 2 m con FAO-56.
4. **Radiación.** ssrd se verificó como radiación solar, se sumó cada día y se convirtió de J m⁻² a MJ m⁻² d⁻¹. Rn es la del pasto de referencia (albedo 0.23), no la radiación neta de la superficie real.
5. **Calor del suelo y presión.** Se aplicó G≈0 a diario; el cálculo mensual directo usó Gi=0.07(Ti+1−Ti−1). Gamma se obtuvo de la presión espacialmente ponderada.
6. **ETo y agregación.** Se calcularon 15,582 días, desde 1981-01-01 hasta 2023-08-30. La mayor diferencia absoluta entre la suma diaria y el cálculo mensual directo fue 0.889 mm en 1997-12; se conserva como señal del error por promediar antes de una ecuación no lineal.

## Control de calidad

- Todos los días retenidos tienen 24 horas; ETo es finita y no negativa.
- La reconstrucción independiente de la ecuación FAO-56 difiere como máximo 3.553e-15 mm/día.
- Quedan 13 celdas y 9.8736% del peso para completar la ponderación de Tarea 1.
