# Sensibilidad POT y comparación con GEV-MLE

Se evaluaron umbrales 90 %, 95 % y 98 %, con declustering de 24 h.

 threshold_percentile  threshold_mm_h  independent_peaks  lambda_events_year     xi   beta
               0.9000          0.1200               1600             74.8204 0.2087 2.0263
               0.9500          0.5300               1523             71.2197 0.2340 1.8742
               0.9800          1.3000               1131             52.8887 0.2606 1.8686

## Comparación de niveles 1 h

 threshold_percentile  T_years  pot_mm_1h  gev_mle_mm_1h  pot_to_gev_ratio
                0.900        2     18.023         18.451             0.977
                0.900        5     23.841         29.042             0.821
                0.900       10     29.043         38.812             0.748
                0.900       25     37.184         55.548             0.669
                0.900       50     44.463         72.174             0.616
                0.900      100     52.875         93.356             0.566
                0.950        2     18.078         18.451             0.980
                0.950        5     24.188         29.042             0.833
                0.950       10     29.764         38.812             0.767
                0.950       25     38.668         55.548             0.696
                0.950       50     46.793         72.174             0.648
                0.950      100     56.349         93.356             0.604
                0.980        2     18.290         18.451             0.991
                0.980        5     24.806         29.042             0.854
                0.980       10     30.879         38.812             0.796
                0.980       25     40.791         55.548             0.734
                0.980       50     50.029         72.174             0.693
                0.980      100     61.095         93.356             0.654

Interpretación: si el cociente POT/GEV cambia mucho entre umbrales, la bonificación es sensible al umbral y no debe sustituir la IDF principal.