# 1.3.3 Budyko — complemento documental y físico

## Alcance

Este complemento **no recalcula** el ajuste de Fu ni las elasticidades. Interpreta
los resultados exploratorios ya verificados para el periodo común 2002–2022:
índice de aridez `φ = 1.098`, índice evaporativo de diagnóstico `(P−Q)/P =
0.540`, `ω = 1.756`, distancia vertical a Budyko (1974) `−0.186` y elasticidad
teórica `1.555`; la elasticidad empírica previamente estimada es `1.488`.

## Evidencia incorporada

El documento técnico de PEOT de julio de 2023 ubica la Bocatoma Racarumi en la
cuenca del río Chancay, la integra al Sistema Hidráulico Mayor Tinajones y señala
que PEOT lo opera (p. 12 impresa). También muestra infraestructura de barrajes,
protección y coordinación de condiciones de operación (pp. 3, 5 y 12).

La nota institucional de PEOT del 19 de diciembre de 2025 informa mantenimiento
de los túneles Chotano y Conchano para el trasvase del río Chotano hacia el valle
Chancay-Lambayeque (pp. 1–2). Es evidencia de conexión hidráulica y de gestión,
no una serie de aportes históricos ni una cuantificación de transferencia.

## Lectura científica prudente

La distancia vertical negativa indica que el cociente diagnóstico `(P−Q)/P` está
por debajo de la curva de Budyko (1974) para el `φ` usado. Esta posición no debe
atribuirse a vegetación, nieve, suelo o regulación de forma aislada: el paquete
local conservado no aporta atributos estáticos verificables de cobertura vegetal,
bosque, nieve/glaciares ni suelo para PE_200907.

Sí hay heterogeneidad altitudinal verificada en las celdas SRTM de Tarea 1
(264–4084 m; media ponderada 2348.98 m), además de estacionalidad y humedad
radicular ya analizadas. Esos factores son hipótesis físicamente plausibles para
explorar cuando existan datos consistentes, pero no explicaciones cuantificadas
de la desviación.

La metadata local de CAMELS-PE clasifica `flow_obs` como **caudal observado** y
no documenta naturalización. Junto con la evidencia de infraestructura/trasvase,
esto obliga a mantener `(P−Q)/P` como diagnóstico exploratorio y no como ET real:
faltan `ΔS` anual, ubicación hidráulica exacta del aforo frente a las obras,
series históricas de trasvases/derivaciones, operación de Tinajones y metodología
de naturalización si existiera.

## Datos requeridos para cerrar la interpretación

1. Ficha CAMELS-PE/SENAMHI de la estación: ubicación, datum, área efectiva y si
   el caudal fue naturalizado, regulado o corregido.
2. Series mensuales/anuales 1981–2023 de trasvases Chotano y Conchano, derivaciones
   de Bocatoma Racarumi, reglas de operación, niveles/volúmenes de almacenamiento.
3. Balance consolidado del numeral 1.2 con ET real y evaluación de `ΔS` anual.
4. Atributos espaciales trazables de uso/cobertura, bosque, suelo, nieve/glaciares
   y, si procede, evolución temporal de cobertura.

## Referencias

- Proyecto Especial Olmos Tinajones (PEOT), Gobierno Regional Lambayeque (2023).
  *Términos de Referencia: Supervisión de la obra Rehabilitación de la Bocatoma
  Racarumi del Sistema Hidráulico Mayor Tinajones*. Chiclayo, julio de 2023.
- Proyecto Especial Olmos Tinajones (PEOT) (2025). *PEOT concluye mantenimiento
  en túneles Chotano y Conchano para asegurar el trasvase de aguas hacia
  Lambayeque*. Nota institucional, 19 de diciembre de 2025.
- Fu, B. P. (1981). On the calculation of the evaporation from land surface.
  *Scientia Atmospherica Sinica*, 5, 23–31.
- Budyko, M. I. (1974). *Climate and Life*. Academic Press.
