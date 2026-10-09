# B3. Kernel-weighted conformal prediction

Seed 0, 5 random splits, up to 4000 unstable and 4000 stable cases per evaluation set. Each cell: miss % / false alarm % (false alarm % of one threshold set on the same cases for the same miss rate; reference only). k_nn = 20, n_eff_min = 5 as in the source.

## alpha = 0.02

| calibration | method | main test | N-2 | N-3 | N-4 | N-5 | N-6 |
|---|---|---|---|---|---|---|---|
| main layer | one threshold | 1.83 / 1.9 (1.9) | 4.23 / 2.9 (2.9) | 5.17 / 4.5 (4.5) | 7.43 / 5.8 (5.8) | 8.00 / 7.9 (7.9) | 8.00 / 8.2 (8.2) |
| main layer | KCP, embedding | 1.18 / 33.5 (2.6) | 1.05 / 38.9 (7.3) | 1.01 / 49.3 (14.1) | 1.14 / 55.9 (21.8) | 0.82 / 62.9 (33.7) | 0.68 / 67.2 (33.9) |
| main layer | KCP, topology | 2.62 / 1.7 (1.4) | 4.16 / 2.9 (2.9) | 5.16 / 4.6 (4.5) | 7.47 / 5.8 (5.7) | 8.04 / 7.8 (7.8) | 8.12 / 8.1 (8.0) |
| main layer | KCP, embedding, k_nn = 100 | 1.39 / 8.6 (2.3) | 1.46 / 12.7 (6.1) | 1.43 / 20.8 (12.0) | 1.87 / 25.8 (17.5) | 1.58 / 32.4 (25.4) | 1.30 / 34.0 (26.2) |
| main layer | KCP, embedding, k_nn = 500 | 1.95 / 3.2 (1.8) | 2.97 / 5.0 (3.7) | 3.64 / 8.1 (6.5) | 5.17 / 10.2 (8.3) | 5.33 / 13.2 (11.7) | 4.84 / 13.6 (12.8) |
| main layer | KCP, embedding, k_nn = 2000 | 1.60 / 3.0 (2.1) | 2.92 / 4.6 (3.7) | 3.70 / 7.3 (6.3) | 5.40 / 9.3 (7.9) | 5.58 / 12.1 (11.2) | 5.16 / 12.6 (12.0) |
| pooled | one threshold | 0.34 / 4.5 (4.2) | 1.07 / 7.5 (7.4) | 1.44 / 12.1 (12.0) | 2.56 / 14.9 (14.7) | 2.50 / 18.2 (18.2) | 2.58 / 20.7 (20.6) |
| pooled | one threshold per layer (labels) | 1.83 / 1.7 (1.7) | 1.98 / 5.1 (5.1) | 1.93 / 9.9 (9.8) | 1.93 / 17.4 (17.3) | 1.86 / 22.1 (21.9) | 2.15 / 22.8 (22.8) |
| pooled | KCP, embedding | 1.10 / 89.3 (2.4) | 1.16 / 90.8 (7.3) | 0.87 / 92.8 (15.1) | 0.68 / 94.7 (29.4) | 0.55 / 95.4 (38.2) | 0.39 / 96.5 (50.9) |
| pooled | KCP, topology | 2.62 / 1.7 (1.2) | 1.84 / 5.3 (5.3) | 1.97 / 9.6 (9.8) | 2.93 / 13.0 (13.4) | 2.76 / 16.9 (17.2) | 2.83 / 19.4 (19.4) |

## alpha = 0.05

| calibration | method | main test | N-2 | N-3 | N-4 | N-5 | N-6 |
|---|---|---|---|---|---|---|---|
| main layer | one threshold | 4.60 / 0.7 (0.7) | 8.49 / 1.1 (1.1) | 10.12 / 2.1 (2.1) | 12.80 / 2.8 (2.8) | 14.37 / 3.8 (3.8) | 13.55 / 4.1 (4.0) |
| main layer | KCP, embedding | 4.24 / 24.1 (0.8) | 4.00 / 29.4 (3.0) | 3.97 / 40.3 (6.1) | 3.92 / 46.7 (11.2) | 3.47 / 54.0 (15.8) | 2.67 / 58.1 (18.4) |
| main layer | KCP, topology | 5.50 / 0.7 (0.6) | 8.51 / 1.1 (1.1) | 10.12 / 2.0 (2.1) | 12.77 / 2.8 (2.9) | 14.41 / 3.7 (3.8) | 13.60 / 4.0 (4.0) |
| main layer | KCP, embedding, k_nn = 100 | 5.73 / 5.8 (0.5) | 6.01 / 8.5 (1.9) | 5.89 / 14.4 (3.9) | 6.28 / 17.6 (7.1) | 5.86 / 22.6 (10.5) | 4.67 / 23.6 (12.9) |
| main layer | KCP, embedding, k_nn = 500 | 8.05 / 2.0 (0.4) | 10.00 / 3.1 (0.8) | 10.45 / 4.8 (2.0) | 12.01 / 6.0 (3.1) | 11.88 / 8.3 (5.1) | 10.87 / 8.5 (5.6) |
| main layer | KCP, embedding, k_nn = 2000 | 8.53 / 1.4 (0.3) | 11.23 / 2.1 (0.7) | 11.65 / 3.4 (1.7) | 14.04 / 4.4 (2.5) | 14.13 / 6.2 (3.8) | 13.06 / 6.3 (4.3) |
| pooled | one threshold | 1.31 / 2.2 (2.2) | 3.08 / 3.7 (3.7) | 3.89 / 6.0 (6.0) | 6.11 / 7.5 (7.5) | 6.53 / 9.7 (9.6) | 6.58 / 11.1 (11.1) |
| pooled | one threshold per layer (labels) | 4.60 / 0.7 (0.7) | 4.77 / 2.5 (2.5) | 4.83 / 4.7 (4.7) | 4.96 / 9.2 (9.1) | 4.98 / 12.2 (12.2) | 5.34 / 13.2 (13.1) |
| pooled | KCP, embedding | 4.01 / 82.3 (0.8) | 3.63 / 85.4 (3.3) | 3.12 / 88.2 (7.0) | 2.53 / 91.1 (14.9) | 2.30 / 92.8 (19.2) | 1.52 / 94.8 (26.6) |
| pooled | KCP, topology | 5.50 / 0.7 (0.6) | 4.81 / 2.3 (2.5) | 5.09 / 4.4 (4.4) | 6.93 / 6.3 (6.5) | 7.18 / 8.6 (8.7) | 7.17 / 10.3 (10.3) |

## N-4 in detail, alpha = 0.02

Late = unstable cases crossing 240 degrees more than 1 s after the decision.

| calibration | method | miss | miss, late | false alarm | reference false alarm | fallback | median n_eff |
|---|---|---|---|---|---|---|---|
| main layer | one threshold | 7.43 | 26.12 | 5.8 | 5.8 | nan % | nan |
| main layer | KCP, embedding | 1.14 | 1.24 | 55.9 | 21.8 | 0.0 % | 95 |
| main layer | KCP, topology | 7.47 | 26.28 | 5.8 | 5.7 | 0.0 % | 3232 |
| main layer | KCP, embedding, k_nn = 100 | 1.87 | 3.80 | 25.8 | 17.5 | 0.0 % | 875 |
| main layer | KCP, embedding, k_nn = 500 | 5.17 | 15.94 | 10.2 | 8.3 | 0.0 % | 2931 |
| main layer | KCP, embedding, k_nn = 2000 | 5.40 | 17.46 | 9.3 | 7.9 | 0.0 % | 3208 |
| pooled | one threshold | 2.56 | 9.09 | 14.9 | 14.7 | nan % | nan |
| pooled | one threshold per layer (labels) | 1.93 | 6.87 | 17.4 | 17.3 | nan % | nan |
| pooled | KCP, embedding | 0.68 | 0.49 | 94.7 | 29.4 | 0.0 % | 516 |
| pooled | KCP, topology | 2.93 | 10.35 | 13.0 | 13.4 | 0.0 % | 22769 |

## One shared threshold at the same N-4 miss rate, alpha = 0.02, main-layer calibration

For each method: its mean miss / false alarm (%) on the main test and N-4, then the same two sets under one threshold shared by all sets and placed on all N-4 cases to give the method's N-4 miss rate (reference, uses the N-4 labels).

| method | main test | N-4 | shared threshold | main test, shared | N-4, shared |
|---|---|---|---|---|---|
| one threshold | 1.83 / 1.9 | 7.43 / 5.8 | 0.241 | 1.82 / 1.8 | 7.43 / 6.1 |
| KCP, embedding | 1.18 / 33.5 | 1.14 / 55.9 | 0.045 | 0.13 / 7.1 | 1.14 / 22.1 |
| KCP, topology | 2.62 / 1.7 | 7.47 / 5.8 | 0.243 | 1.82 / 1.8 | 7.47 / 6.1 |
| KCP, embedding, k_nn = 100 | 1.39 / 8.6 | 1.87 / 25.8 | 0.048 | 0.28 / 5.7 | 1.86 / 17.7 |
| KCP, embedding, k_nn = 500 | 1.95 / 3.2 | 5.17 / 10.2 | 0.124 | 1.00 / 2.7 | 5.17 / 8.8 |
| KCP, embedding, k_nn = 2000 | 1.60 / 3.0 | 5.40 / 9.3 | 0.134 | 1.10 / 2.6 | 5.39 / 8.4 |
