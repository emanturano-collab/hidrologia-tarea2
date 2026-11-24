# Validación desde carpeta limpia

Se copió el paquete provisional a `output/clean_test/` y se ejecutó
`codigo/punto2/auditar_pre_informe.py` sin depender de rutas absolutas del
repositorio original. El resultado fue **10/10 verificaciones OK**:

- área y outlet de la microcuenca;
- diámetro y capacidad hidráulica;
- riesgo Monte Carlo y volumen/profundidad del tanque;
- sensibilidad POT;
- resultados 2.2–2.3 (bootstrap e IDF–KOSTRA);
- presencia de los scripts principales de cálculo.

El texto completo generado se conserva en
`output/clean_test/productos/punto2/auditoria_pre_informe_resultado.md`.
