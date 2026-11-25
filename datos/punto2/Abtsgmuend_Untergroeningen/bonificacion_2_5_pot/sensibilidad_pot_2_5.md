# Sensibilidad POT y comparación con GEV-MLE

Se evaluaron umbrales 90 %, 95 % y 98 %, con declustering de 24 h.

 threshold_percentile  threshold_mm_h  independent_peaks  lambda_events_year     xi   beta
               0.9000          0.1100               1566             74.5727 0.2125 2.0246
               0.9500          0.5300               1491             71.0012 0.2367 1.8726
               0.9800          1.3000               1111             52.9057 0.2655 1.8584

## Comparación de niveles 1 h

 threshold_percentile  T_years  pot_mm_1h  gev_mle_mm_1h  pot_to_gev_ratio
                0.900        2     18.179         18.451             0.985
                0.900        5     24.110         29.042             0.830
                0.900       10     29.430         38.812             0.758
                0.900       25     37.780         55.548             0.680
                0.900       50     45.269         72.174             0.627
                0.900      100     53.946         93.356             0.578
                0.950        2     18.184         18.451             0.986
                0.950        5     24.375         29.042             0.839
                0.950       10     30.037         38.812             0.774
                0.950       25     39.098         55.548             0.704
                0.950       50     47.383         72.174             0.657
                0.950      100     57.146         93.356             0.612
                0.980        2     18.432         18.451             0.999
                0.980        5     25.078         29.042             0.864
                0.980       10     31.297         38.812             0.806
                0.980       25     41.486         55.548             0.747
                0.980       50     51.021         72.174             0.707
                0.980      100     62.481         93.356             0.669

Interpretación: si el cociente POT/GEV cambia mucho entre umbrales, la bonificación es sensible al umbral y no debe sustituir la IDF principal.