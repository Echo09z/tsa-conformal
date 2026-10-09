# A1. Calibration on the main layer only

## alpha = 0.01

Miss rate (%) of the unstable samples, mean over seeds (and splits); [5th, 95th percentile] over seeds x splits; false-alarm rate (%) in the last column of each source.

| evaluation set | val | test-half | test-half-1 (strict) | false alarm, test-half |
|---|---|---|---|---|
| main test (other half) |  | 0.96 [0.54, 1.41] | 0.87 [0.33, 1.49] | 2.73 |
| main test (all) | 0.89 |  |  | |
| N-2 | 2.35 | 2.46 [1.96, 2.96] | 2.29 [1.41, 3.37] | 4.34 |
| N-3 | 2.87 | 2.99 [2.46, 3.59] | 2.81 [1.89, 4.00] | 7.21 |
| N-4 | 4.60 | 4.74 [3.88, 5.55] | 4.48 [3.06, 6.06] | 9.74 |
| N-5 | 4.70 | 4.89 [3.90, 5.91] | 4.61 [3.06, 6.43] | 12.86 |
| N-6 | 4.73 | 4.92 [3.89, 5.84] | 4.61 [3.01, 6.32] | 13.68 |
| held-out N-1 | 3.14 | 3.43 [2.75, 4.20] | 3.00 [1.50, 4.48] | 2.87 |

## alpha = 0.02

Miss rate (%) of the unstable samples, mean over seeds (and splits); [5th, 95th percentile] over seeds x splits; false-alarm rate (%) in the last column of each source.

| evaluation set | val | test-half | test-half-1 (strict) | false alarm, test-half |
|---|---|---|---|---|
| main test (other half) |  | 1.98 [1.42, 2.66] | 1.93 [1.10, 2.96] | 1.64 |
| main test (all) | 1.87 |  |  | |
| N-2 | 4.16 | 4.35 [3.85, 4.99] | 4.24 [3.03, 5.39] | 2.70 |
| N-3 | 4.91 | 5.08 [4.46, 5.77] | 4.99 [3.61, 6.30] | 4.53 |
| N-4 | 7.14 | 7.41 [6.63, 8.45] | 7.27 [5.54, 9.08] | 6.36 |
| N-5 | 7.54 | 7.80 [6.88, 8.89] | 7.64 [5.68, 9.67] | 8.50 |
| N-6 | 7.48 | 7.72 [6.91, 8.85] | 7.54 [5.71, 9.25] | 9.03 |
| held-out N-1 | 5.22 | 5.42 [4.77, 6.31] | 5.24 [3.93, 6.76] | 1.78 |

## alpha = 0.05

Miss rate (%) of the unstable samples, mean over seeds (and splits); [5th, 95th percentile] over seeds x splits; false-alarm rate (%) in the last column of each source.

| evaluation set | val | test-half | test-half-1 (strict) | false alarm, test-half |
|---|---|---|---|---|
| main test (other half) |  | 4.99 [3.93, 6.13] | 5.13 [3.60, 6.82] | 0.66 |
| main test (all) | 4.67 |  |  | |
| N-2 | 7.86 | 8.17 [7.17, 9.00] | 8.36 [6.59, 9.79] | 1.23 |
| N-3 | 9.11 | 9.47 [8.30, 10.59] | 9.72 [7.80, 11.44] | 2.24 |
| N-4 | 12.09 | 12.44 [10.98, 13.78] | 12.69 [10.36, 14.65] | 3.20 |
| N-5 | 12.82 | 13.21 [11.48, 15.04] | 13.46 [10.90, 15.78] | 4.37 |
| N-6 | 12.25 | 12.61 [11.06, 14.12] | 12.82 [10.47, 14.81] | 4.79 |
| held-out N-1 | 9.51 | 10.15 [9.17, 11.32] | 10.18 [7.87, 12.23] | 0.73 |

## alpha = 0.10

Miss rate (%) of the unstable samples, mean over seeds (and splits); [5th, 95th percentile] over seeds x splits; false-alarm rate (%) in the last column of each source.

| evaluation set | val | test-half | test-half-1 (strict) | false alarm, test-half |
|---|---|---|---|---|
| main test (other half) |  | 9.99 [8.53, 11.43] | 10.22 [7.91, 12.43] | 0.21 |
| main test (all) | 9.89 |  |  | |
| N-2 | 13.58 | 13.60 [12.72, 14.40] | 14.03 [11.99, 15.65] | 0.50 |
| N-3 | 15.54 | 15.53 [14.25, 16.67] | 15.97 [13.68, 18.00] | 0.94 |
| N-4 | 18.75 | 18.76 [17.15, 20.05] | 19.27 [16.68, 21.50] | 1.45 |
| N-5 | 19.57 | 19.54 [17.61, 21.07] | 20.03 [17.14, 22.36] | 1.96 |
| N-6 | 18.32 | 18.32 [16.47, 19.66] | 18.78 [16.01, 21.00] | 2.31 |
| held-out N-1 | 16.34 | 16.64 [15.57, 17.67] | 16.49 [14.48, 18.44] | 0.28 |

## Uncertainty of the layer miss rates (alpha = 0.02, validation calibration)

Seed-mean miss rate (%) with a 95 % percentile interval from resampling whole topologies (1000 resamples).

| layer | miss | 95 % interval | topologies |
|---|---|---|---|
| N-2 | 4.16 | [3.46, 5.05] | 199 |
| N-3 | 4.91 | [4.38, 5.43] | 196 |
| N-4 | 7.14 | [6.43, 7.93] | 194 |
| N-5 | 7.54 | [6.73, 8.49] | 185 |
| N-6 | 7.48 | [6.66, 8.48] | 165 |
