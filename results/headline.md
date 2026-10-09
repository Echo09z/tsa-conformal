# Headline numbers, alpha = 0.02

Per seed: mean over random calibration / test splits; then mean ± standard deviation over the seeds (five for the proposed model, three for the model trained without five N-1 topologies). %.

| evaluation set | miss, main-layer calibration | false alarm, main-layer calibration | miss, N-2 calibration | miss, stratified | false alarm, stratified | referred, two-sided stratified |
|---|---|---|---|---|---|---|
| main test (other half) | 1.97 ± 0.07 | 1.62 ± 0.09 | – | – | – | – |
| held-out N-1 | 5.42 ± 0.35 | 1.78 ± 0.14 | – | – | – | – |
| N-2 | 4.35 ± 0.26 | 2.70 ± 0.08 | – | 2.06 ± 0.04 | 4.92 ± 0.19 | 3.11 ± 0.17 |
| N-3 | 5.08 ± 0.32 | 4.53 ± 0.15 | 2.51 ± 0.05 | 1.98 ± 0.06 | 9.53 ± 0.40 | 7.64 ± 0.20 |
| N-4 | 7.41 ± 0.47 | 6.36 ± 0.42 | 4.09 ± 0.14 | 2.03 ± 0.05 | 17.08 ± 0.51 | 14.86 ± 0.48 |
| N-5 | 7.80 ± 0.61 | 8.50 ± 0.62 | 4.18 ± 0.22 | 2.00 ± 0.04 | 22.52 ± 0.58 | 19.41 ± 0.35 |
| N-6 | 7.72 ± 0.51 | 9.03 ± 0.62 | 4.18 ± 0.17 | 2.01 ± 0.02 | 23.55 ± 0.68 | 19.99 ± 0.48 |
