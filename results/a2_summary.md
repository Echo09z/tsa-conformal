# A2. Calibration stratified by N-k layer

Minimum calibration size for a finite threshold: alpha 0.01: 99, alpha 0.02: 49, alpha 0.05: 19, alpha 0.10: 9.

## Half of each layer's topologies for calibration, alpha = 0.02

Miss rate (%) on the other topologies of the layer: mean, [5th, 95th percentile] and share of seed x split draws above alpha; false-alarm rate (%).

| layer | variant | miss | 5th-95th | P(miss > alpha) | false alarm |
|---|---|---|---|---|---|
| N-2 | all samples | 2.06 | [1.18, 3.01] | 53 % | 4.92 |
| N-2 | one per topology | 2.34 | [0.31, 5.48] | 51 % | 6.05 |
| N-3 | all samples | 1.98 | [1.50, 2.53] | 47 % | 9.53 |
| N-3 | one per topology | 0.78 | [0.04, 2.30] | 8 % | 33.14 |
| N-4 | all samples | 2.03 | [1.43, 2.64] | 50 % | 17.08 |
| N-4 | one per topology | 1.00 | [0.03, 3.33] | 14 % | 41.67 |
| N-5 | all samples | 2.00 | [1.36, 2.73] | 50 % | 22.52 |
| N-5 | one per topology | 0.99 | [0.03, 3.30] | 16 % | 49.26 |
| N-6 | all samples | 2.01 | [1.48, 2.69] | 45 % | 23.55 |
| N-6 | one per topology | 1.04 | [0.04, 3.47] | 13 % | 47.09 |

## Data cost: miss rate against the number of calibration topologies, alpha = 0.02

All samples of the calibration topologies; mean [5th, 95th percentile] of the miss rate (%), share of draws above alpha and mean false-alarm rate (%). The strict variant needs at least 49 topologies with an unstable sample and is reported for m >= 50.

| layer | m | miss | 5th-95th | P(miss > alpha) | false alarm | strict: miss | strict: P(> alpha) | strict: finite |
|---|---|---|---|---|---|---|---|---|
| N-2 | 5 (=5) | 2.22 | [0.53, 4.50] | 49 % | 6.52 | - | - | 0 % |
| N-2 | 10 (=10) | 2.23 | [0.67, 3.93] | 58 % | 5.46 | - | - | 0 % |
| N-2 | 20 (=20) | 2.12 | [0.65, 3.44] | 56 % | 5.16 | - | - | 0 % |
| N-2 | 50 (=50) | 2.09 | [1.00, 3.09] | 60 % | 4.98 | 2.31 | 43 % | 100 % |
| N-2 | half (=100) | 2.06 | [1.18, 3.01] | 53 % | 4.92 | 2.34 | 51 % | 100 % |
| N-3 | 5 (=5) | 2.00 | [0.60, 3.70] | 42 % | 11.18 | - | - | 0 % |
| N-3 | 10 (=10) | 2.03 | [1.00, 3.63] | 46 % | 10.04 | - | - | 0 % |
| N-3 | 20 (=20) | 2.04 | [1.18, 3.03] | 50 % | 9.69 | - | - | 0 % |
| N-3 | 50 (=50) | 1.99 | [1.37, 2.64] | 47 % | 9.66 | 2.03 | 42 % | 100 % |
| N-3 | half (=98) | 1.98 | [1.50, 2.53] | 47 % | 9.53 | 0.78 | 8 % | 100 % |
| N-4 | 5 (=5) | 2.08 | [0.71, 3.92] | 44 % | 18.85 | - | - | 0 % |
| N-4 | 10 (=10) | 2.04 | [0.87, 3.20] | 48 % | 17.87 | - | - | 0 % |
| N-4 | 20 (=20) | 2.02 | [1.14, 3.26] | 44 % | 17.52 | - | - | 0 % |
| N-4 | 50 (=50) | 1.98 | [1.35, 2.72] | 44 % | 17.27 | 1.82 | 34 % | 100 % |
| N-4 | half (=97) | 2.03 | [1.43, 2.64] | 50 % | 17.08 | 1.00 | 14 % | 100 % |
| N-5 | 5 (=5) | 2.30 | [0.67, 4.73] | 49 % | 23.35 | - | - | 0 % |
| N-5 | 10 (=10) | 2.06 | [0.95, 3.55] | 46 % | 23.32 | - | - | 0 % |
| N-5 | 20 (=20) | 2.04 | [1.13, 3.12] | 49 % | 22.77 | - | - | 0 % |
| N-5 | 50 (=50) | 2.03 | [1.31, 2.79] | 48 % | 22.51 | 1.80 | 34 % | 100 % |
| N-5 | half (=92) | 2.00 | [1.36, 2.73] | 50 % | 22.52 | 0.99 | 16 % | 100 % |
| N-6 | 5 (=5) | 2.21 | [0.61, 4.49] | 48 % | 25.03 | - | - | 0 % |
| N-6 | 10 (=10) | 2.07 | [0.99, 3.40] | 49 % | 24.04 | - | - | 0 % |
| N-6 | 20 (=20) | 2.05 | [1.20, 2.98] | 48 % | 23.59 | - | - | 0 % |
| N-6 | 50 (=50) | 2.04 | [1.35, 2.78] | 52 % | 23.36 | 1.77 | 34 % | 100 % |
| N-6 | half (=82) | 2.01 | [1.48, 2.69] | 45 % | 23.55 | 1.04 | 13 % | 100 % |

## B1. Calibration on half of the N-2 topologies only, alpha = 0.02

| evaluation layer | miss | 5th-95th | P(miss > alpha) | false alarm |
|---|---|---|---|---|
| N-3 | 2.51 | [1.98, 3.06] | 95 % | 8.22 |
| N-4 | 4.09 | [3.37, 4.93] | 100 % | 10.93 |
| N-5 | 4.18 | [3.36, 5.24] | 100 % | 14.45 |
| N-6 | 4.18 | [3.37, 5.17] | 100 % | 15.35 |
