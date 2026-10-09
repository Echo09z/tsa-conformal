# A4. Calibration-conditional thresholds

delta = 0.05. Minimum number of exchangeable calibration values for a finite conditional threshold: alpha 0.01: 299, alpha 0.02: 149, alpha 0.05: 59, alpha 0.10: 29.

Per row, over seeds x splits: mean miss rate (%), share of single calibrations whose miss rate exceeds alpha, per case and per cluster (target <= delta for the conditional variants), mean false-alarm rate (%), share of draws with a finite threshold. Draws without a finite threshold alarm on every case.

## alpha = 0.01

| evaluation | calibration clusters | variant | calibration values | miss | P(miss > alpha) | P(per-cluster miss > alpha) | false alarm | finite |
|---|---|---|---|---|---|---|---|---|
| main test | half (=1020) | marginal, all faults | 3453 | 0.99 | 44 % | 49 % | 2.7 | 100 % |
| main test | half (=1020) | conditional, all faults | 3453 | 0.74 | 10 % | 14 % | 3.2 | 100 % |
| main test | half (=1020) | marginal, one per cluster | 879 | 0.86 | 27 % | 32 % | 2.9 | 100 % |
| main test | half (=1020) | conditional, one per cluster | 879 | 0.42 | 2 % | 3 % | 4.6 | 100 % |
| N-2 | half (=100) | marginal, all faults | 6416 | 1.01 | 48 % | 34 % | 7.6 | 100 % |
| N-2 | half (=100) | conditional, all faults | 6416 | 0.81 | 30 % | 14 % | 8.6 | 100 % |
| N-2 | half (=100) | marginal, one per cluster | 100 | 1.12 | 40 % | 35 % | 19.2 | 100 % |
| N-2 | half (=100) | conditional, one per cluster | 100 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-2 | 150 (=150) | marginal, all faults | 9624 | 1.00 | 38 % | 34 % | 7.5 | 100 % |
| N-2 | 150 (=150) | conditional, all faults | 9624 | 0.84 | 28 % | 22 % | 8.3 | 100 % |
| N-2 | 150 (=150) | marginal, one per cluster | 150 | 0.73 | 28 % | 21 % | 24.0 | 100 % |
| N-2 | 150 (=150) | conditional, one per cluster | 150 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-3 | half (=98) | marginal, all faults | 7334 | 1.01 | 50 % | 67 % | 14.4 | 100 % |
| N-3 | half (=98) | conditional, all faults | 7334 | 0.83 | 17 % | 30 % | 16.1 | 100 % |
| N-3 | half (=98) | marginal, one per cluster | 98 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-3 | half (=98) | conditional, one per cluster | 98 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-3 | 150 (=150) | marginal, all faults | 11164 | 0.97 | 45 % | 54 % | 14.4 | 100 % |
| N-3 | 150 (=150) | conditional, all faults | 11164 | 0.83 | 21 % | 36 % | 15.8 | 100 % |
| N-3 | 150 (=150) | marginal, one per cluster | 150 | 0.61 | 20 % | 23 % | 39.0 | 100 % |
| N-3 | 150 (=150) | conditional, one per cluster | 150 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-4 | half (=97) | marginal, all faults | 8766 | 1.02 | 45 % | 59 % | 24.7 | 100 % |
| N-4 | half (=97) | conditional, all faults | 8766 | 0.85 | 21 % | 29 % | 27.4 | 100 % |
| N-4 | half (=97) | marginal, one per cluster | 97 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-4 | half (=97) | conditional, one per cluster | 97 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-4 | 150 (=150) | marginal, all faults | 13574 | 1.01 | 49 % | 56 % | 24.5 | 100 % |
| N-4 | 150 (=150) | conditional, all faults | 13574 | 0.87 | 31 % | 37 % | 26.8 | 100 % |
| N-4 | 150 (=150) | marginal, one per cluster | 150 | 0.63 | 23 % | 24 % | 52.3 | 100 % |
| N-4 | 150 (=150) | conditional, one per cluster | 150 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-5 | half (=92) | marginal, all faults | 8992 | 0.99 | 42 % | 60 % | 31.6 | 100 % |
| N-5 | half (=92) | conditional, all faults | 8992 | 0.83 | 25 % | 39 % | 34.9 | 100 % |
| N-5 | half (=92) | marginal, one per cluster | 92 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-5 | half (=92) | conditional, one per cluster | 92 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-5 | 150 (=150) | marginal, all faults | 14751 | 1.02 | 53 % | 66 % | 31.0 | 100 % |
| N-5 | 150 (=150) | conditional, all faults | 14751 | 0.89 | 31 % | 53 % | 33.4 | 100 % |
| N-5 | 150 (=150) | marginal, one per cluster | 150 | 0.56 | 20 % | 23 % | 58.2 | 100 % |
| N-5 | 150 (=150) | conditional, one per cluster | 150 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-6 | half (=82) | marginal, all faults | 8592 | 0.99 | 48 % | 64 % | 33.0 | 100 % |
| N-6 | half (=82) | conditional, all faults | 8592 | 0.82 | 24 % | 34 % | 36.4 | 100 % |
| N-6 | half (=82) | marginal, one per cluster | 82 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-6 | half (=82) | conditional, one per cluster | 82 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-6 | 150 (=150) | marginal, all faults | 15749 | 1.01 | 44 % | 57 % | 32.7 | 100 % |
| N-6 | 150 (=150) | conditional, all faults | 15749 | 0.90 | 34 % | 44 % | 35.1 | 100 % |
| N-6 | 150 (=150) | marginal, one per cluster | 150 | 0.58 | 18 % | 22 % | 59.3 | 100 % |
| N-6 | 150 (=150) | conditional, one per cluster | 150 | 0.00 | 0 % | 0 % | 100.0 | 0 % |

## alpha = 0.02

| evaluation | calibration clusters | variant | calibration values | miss | P(miss > alpha) | P(per-cluster miss > alpha) | false alarm | finite |
|---|---|---|---|---|---|---|---|---|
| main test | half (=1020) | marginal, all faults | 3453 | 2.00 | 49 % | 44 % | 1.6 | 100 % |
| main test | half (=1020) | conditional, all faults | 3453 | 1.63 | 12 % | 14 % | 1.9 | 100 % |
| main test | half (=1020) | marginal, one per cluster | 879 | 1.95 | 41 % | 39 % | 1.7 | 100 % |
| main test | half (=1020) | conditional, one per cluster | 879 | 1.21 | 4 % | 5 % | 2.4 | 100 % |
| N-2 | half (=100) | marginal, all faults | 6416 | 1.97 | 46 % | 25 % | 5.0 | 100 % |
| N-2 | half (=100) | conditional, all faults | 6416 | 1.70 | 30 % | 10 % | 5.5 | 100 % |
| N-2 | half (=100) | marginal, one per cluster | 100 | 2.35 | 52 % | 43 % | 6.1 | 100 % |
| N-2 | half (=100) | conditional, one per cluster | 100 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-2 | 150 (=150) | marginal, all faults | 9624 | 1.98 | 38 % | 28 % | 5.0 | 100 % |
| N-2 | 150 (=150) | conditional, all faults | 9624 | 1.76 | 29 % | 15 % | 5.4 | 100 % |
| N-2 | 150 (=150) | marginal, one per cluster | 150 | 2.12 | 46 % | 40 % | 5.6 | 100 % |
| N-2 | 150 (=150) | conditional, one per cluster | 150 | 0.73 | 8 % | 5 % | 24.0 | 100 % |
| N-3 | half (=98) | marginal, all faults | 7334 | 2.02 | 55 % | 62 % | 9.5 | 100 % |
| N-3 | half (=98) | conditional, all faults | 7334 | 1.76 | 18 % | 31 % | 10.4 | 100 % |
| N-3 | half (=98) | marginal, one per cluster | 98 | 0.89 | 10 % | 11 % | 31.8 | 100 % |
| N-3 | half (=98) | conditional, one per cluster | 98 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-3 | 150 (=150) | marginal, all faults | 11164 | 1.96 | 46 % | 52 % | 9.6 | 100 % |
| N-3 | 150 (=150) | conditional, all faults | 11164 | 1.75 | 25 % | 33 % | 10.3 | 100 % |
| N-3 | 150 (=150) | marginal, one per cluster | 150 | 2.00 | 46 % | 47 % | 11.4 | 100 % |
| N-3 | 150 (=150) | conditional, one per cluster | 150 | 0.61 | 4 % | 4 % | 39.0 | 100 % |
| N-4 | half (=97) | marginal, all faults | 8766 | 2.05 | 49 % | 60 % | 17.1 | 100 % |
| N-4 | half (=97) | conditional, all faults | 8766 | 1.80 | 24 % | 30 % | 18.3 | 100 % |
| N-4 | half (=97) | marginal, one per cluster | 97 | 0.83 | 8 % | 9 % | 45.3 | 100 % |
| N-4 | half (=97) | conditional, one per cluster | 97 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-4 | 150 (=150) | marginal, all faults | 13574 | 2.02 | 50 % | 57 % | 17.0 | 100 % |
| N-4 | 150 (=150) | conditional, all faults | 13574 | 1.82 | 31 % | 37 % | 18.0 | 100 % |
| N-4 | 150 (=150) | marginal, one per cluster | 150 | 2.05 | 46 % | 48 % | 20.1 | 100 % |
| N-4 | 150 (=150) | conditional, one per cluster | 150 | 0.63 | 6 % | 6 % | 52.3 | 100 % |
| N-5 | half (=92) | marginal, all faults | 8992 | 1.97 | 44 % | 58 % | 22.6 | 100 % |
| N-5 | half (=92) | conditional, all faults | 8992 | 1.73 | 24 % | 31 % | 24.0 | 100 % |
| N-5 | half (=92) | marginal, one per cluster | 92 | 0.92 | 12 % | 12 % | 50.1 | 100 % |
| N-5 | half (=92) | conditional, one per cluster | 92 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-5 | 150 (=150) | marginal, all faults | 14751 | 2.03 | 51 % | 64 % | 22.3 | 100 % |
| N-5 | 150 (=150) | conditional, all faults | 14751 | 1.83 | 33 % | 47 % | 23.4 | 100 % |
| N-5 | 150 (=150) | marginal, one per cluster | 150 | 1.88 | 39 % | 44 % | 26.4 | 100 % |
| N-5 | 150 (=150) | conditional, one per cluster | 150 | 0.56 | 3 % | 5 % | 58.2 | 100 % |
| N-6 | half (=82) | marginal, all faults | 8592 | 1.96 | 43 % | 65 % | 23.7 | 100 % |
| N-6 | half (=82) | conditional, all faults | 8592 | 1.72 | 23 % | 41 % | 25.2 | 100 % |
| N-6 | half (=82) | marginal, one per cluster | 82 | 1.04 | 17 % | 18 % | 47.7 | 100 % |
| N-6 | half (=82) | conditional, one per cluster | 82 | 0.00 | 0 % | 0 % | 100.0 | 0 % |
| N-6 | 150 (=150) | marginal, all faults | 15749 | 2.00 | 44 % | 59 % | 23.4 | 100 % |
| N-6 | 150 (=150) | conditional, all faults | 15749 | 1.83 | 36 % | 46 % | 24.5 | 100 % |
| N-6 | 150 (=150) | marginal, one per cluster | 150 | 1.91 | 36 % | 42 % | 27.4 | 100 % |
| N-6 | 150 (=150) | conditional, one per cluster | 150 | 0.58 | 4 % | 5 % | 59.3 | 100 % |

## alpha = 0.05

| evaluation | calibration clusters | variant | calibration values | miss | P(miss > alpha) | P(per-cluster miss > alpha) | false alarm | finite |
|---|---|---|---|---|---|---|---|---|
| main test | half (=1020) | marginal, all faults | 3453 | 5.00 | 48 % | 30 % | 0.7 | 100 % |
| main test | half (=1020) | conditional, all faults | 3453 | 4.40 | 13 % | 6 % | 0.8 | 100 % |
| main test | half (=1020) | marginal, one per cluster | 879 | 5.23 | 59 % | 42 % | 0.6 | 100 % |
| main test | half (=1020) | conditional, one per cluster | 879 | 3.94 | 9 % | 8 % | 0.9 | 100 % |
| N-2 | half (=100) | marginal, all faults | 6416 | 4.96 | 47 % | 21 % | 2.3 | 100 % |
| N-2 | half (=100) | conditional, all faults | 6416 | 4.51 | 28 % | 9 % | 2.6 | 100 % |
| N-2 | half (=100) | marginal, one per cluster | 100 | 5.47 | 52 % | 45 % | 2.4 | 100 % |
| N-2 | half (=100) | conditional, one per cluster | 100 | 2.35 | 8 % | 5 % | 6.1 | 100 % |
| N-2 | 150 (=150) | marginal, all faults | 9624 | 4.95 | 44 % | 24 % | 2.3 | 100 % |
| N-2 | 150 (=150) | conditional, all faults | 9624 | 4.60 | 32 % | 12 % | 2.5 | 100 % |
| N-2 | 150 (=150) | marginal, one per cluster | 150 | 4.93 | 44 % | 32 % | 2.5 | 100 % |
| N-2 | 150 (=150) | conditional, one per cluster | 150 | 2.12 | 3 % | 2 % | 5.6 | 100 % |
| N-3 | half (=98) | marginal, all faults | 7334 | 5.05 | 55 % | 58 % | 4.6 | 100 % |
| N-3 | half (=98) | conditional, all faults | 7334 | 4.64 | 22 % | 32 % | 5.0 | 100 % |
| N-3 | half (=98) | marginal, one per cluster | 98 | 3.98 | 24 % | 25 % | 6.6 | 100 % |
| N-3 | half (=98) | conditional, one per cluster | 98 | 1.90 | 4 % | 4 % | 13.8 | 100 % |
| N-3 | 150 (=150) | marginal, all faults | 11164 | 4.95 | 47 % | 49 % | 4.6 | 100 % |
| N-3 | 150 (=150) | conditional, all faults | 11164 | 4.62 | 28 % | 31 % | 5.0 | 100 % |
| N-3 | 150 (=150) | marginal, one per cluster | 150 | 4.56 | 33 % | 34 % | 5.5 | 100 % |
| N-3 | 150 (=150) | conditional, one per cluster | 150 | 2.00 | 3 % | 4 % | 11.4 | 100 % |
| N-4 | half (=97) | marginal, all faults | 8766 | 5.12 | 54 % | 55 % | 9.2 | 100 % |
| N-4 | half (=97) | conditional, all faults | 8766 | 4.72 | 34 % | 32 % | 9.9 | 100 % |
| N-4 | half (=97) | marginal, one per cluster | 97 | 3.86 | 24 % | 26 % | 13.0 | 100 % |
| N-4 | half (=97) | conditional, one per cluster | 97 | 1.81 | 3 % | 3 % | 23.9 | 100 % |
| N-4 | 150 (=150) | marginal, all faults | 13574 | 4.98 | 49 % | 49 % | 9.3 | 100 % |
| N-4 | 150 (=150) | conditional, all faults | 13574 | 4.68 | 32 % | 36 % | 9.8 | 100 % |
| N-4 | 150 (=150) | marginal, one per cluster | 150 | 4.73 | 39 % | 41 % | 10.4 | 100 % |
| N-4 | 150 (=150) | conditional, one per cluster | 150 | 2.05 | 3 % | 4 % | 20.1 | 100 % |
| N-5 | half (=92) | marginal, all faults | 8992 | 4.95 | 46 % | 60 % | 12.6 | 100 % |
| N-5 | half (=92) | conditional, all faults | 8992 | 4.60 | 28 % | 41 % | 13.4 | 100 % |
| N-5 | half (=92) | marginal, one per cluster | 92 | 4.13 | 33 % | 36 % | 16.3 | 100 % |
| N-5 | half (=92) | conditional, one per cluster | 92 | 0.92 | 2 % | 2 % | 50.1 | 100 % |
| N-5 | 150 (=150) | marginal, all faults | 14751 | 5.05 | 53 % | 67 % | 12.5 | 100 % |
| N-5 | 150 (=150) | conditional, all faults | 14751 | 4.75 | 40 % | 51 % | 13.1 | 100 % |
| N-5 | 150 (=150) | marginal, one per cluster | 150 | 4.49 | 33 % | 39 % | 14.5 | 100 % |
| N-5 | 150 (=150) | conditional, one per cluster | 150 | 1.88 | 2 % | 2 % | 26.4 | 100 % |
| N-6 | half (=82) | marginal, all faults | 8592 | 4.90 | 42 % | 70 % | 13.7 | 100 % |
| N-6 | half (=82) | conditional, all faults | 8592 | 4.53 | 23 % | 43 % | 14.5 | 100 % |
| N-6 | half (=82) | marginal, one per cluster | 82 | 4.12 | 29 % | 33 % | 16.7 | 100 % |
| N-6 | half (=82) | conditional, one per cluster | 82 | 1.04 | 0 % | 1 % | 47.7 | 100 % |
| N-6 | 150 (=150) | marginal, all faults | 15749 | 5.00 | 46 % | 62 % | 13.5 | 100 % |
| N-6 | 150 (=150) | conditional, all faults | 15749 | 4.71 | 35 % | 51 % | 14.1 | 100 % |
| N-6 | 150 (=150) | marginal, one per cluster | 150 | 4.33 | 32 % | 39 % | 15.6 | 100 % |
| N-6 | 150 (=150) | conditional, one per cluster | 150 | 1.91 | 2 % | 4 % | 27.4 | 100 % |

## alpha = 0.10

| evaluation | calibration clusters | variant | calibration values | miss | P(miss > alpha) | P(per-cluster miss > alpha) | false alarm | finite |
|---|---|---|---|---|---|---|---|---|
| main test | half (=1020) | marginal, all faults | 3453 | 10.03 | 48 % | 28 % | 0.2 | 100 % |
| main test | half (=1020) | conditional, all faults | 3453 | 9.20 | 18 % | 6 % | 0.3 | 100 % |
| main test | half (=1020) | marginal, one per cluster | 879 | 10.43 | 62 % | 42 % | 0.2 | 100 % |
| main test | half (=1020) | conditional, one per cluster | 879 | 8.88 | 16 % | 7 % | 0.3 | 100 % |
| N-2 | half (=100) | marginal, all faults | 6416 | 9.92 | 47 % | 25 % | 0.9 | 100 % |
| N-2 | half (=100) | conditional, all faults | 6416 | 9.32 | 32 % | 10 % | 1.0 | 100 % |
| N-2 | half (=100) | marginal, one per cluster | 100 | 10.47 | 53 % | 42 % | 0.9 | 100 % |
| N-2 | half (=100) | conditional, one per cluster | 100 | 5.47 | 5 % | 2 % | 2.4 | 100 % |
| N-2 | 150 (=150) | marginal, all faults | 9624 | 9.97 | 48 % | 26 % | 0.9 | 100 % |
| N-2 | 150 (=150) | conditional, all faults | 9624 | 9.48 | 33 % | 16 % | 1.0 | 100 % |
| N-2 | 150 (=150) | marginal, one per cluster | 150 | 10.60 | 56 % | 46 % | 0.9 | 100 % |
| N-2 | 150 (=150) | conditional, one per cluster | 150 | 6.34 | 5 % | 2 % | 1.9 | 100 % |
| N-3 | half (=98) | marginal, all faults | 7334 | 10.03 | 51 % | 62 % | 2.1 | 100 % |
| N-3 | half (=98) | conditional, all faults | 7334 | 9.46 | 25 % | 35 % | 2.2 | 100 % |
| N-3 | half (=98) | marginal, one per cluster | 98 | 9.03 | 33 % | 34 % | 2.7 | 100 % |
| N-3 | half (=98) | conditional, one per cluster | 98 | 5.02 | 3 % | 4 % | 5.3 | 100 % |
| N-3 | 150 (=150) | marginal, all faults | 11164 | 9.93 | 46 % | 48 % | 2.1 | 100 % |
| N-3 | 150 (=150) | conditional, all faults | 11164 | 9.47 | 28 % | 34 % | 2.2 | 100 % |
| N-3 | 150 (=150) | marginal, one per cluster | 150 | 9.54 | 40 % | 44 % | 2.4 | 100 % |
| N-3 | 150 (=150) | conditional, one per cluster | 150 | 5.85 | 4 % | 4 % | 4.3 | 100 % |
| N-4 | half (=97) | marginal, all faults | 8766 | 10.16 | 54 % | 52 % | 4.4 | 100 % |
| N-4 | half (=97) | conditional, all faults | 8766 | 9.64 | 35 % | 34 % | 4.7 | 100 % |
| N-4 | half (=97) | marginal, one per cluster | 97 | 9.26 | 36 % | 36 % | 5.6 | 100 % |
| N-4 | half (=97) | conditional, one per cluster | 97 | 4.84 | 4 % | 4 % | 10.8 | 100 % |
| N-4 | 150 (=150) | marginal, all faults | 13574 | 10.02 | 50 % | 52 % | 4.4 | 100 % |
| N-4 | 150 (=150) | conditional, all faults | 13574 | 9.59 | 38 % | 35 % | 4.7 | 100 % |
| N-4 | 150 (=150) | marginal, one per cluster | 150 | 10.15 | 46 % | 48 % | 4.6 | 100 % |
| N-4 | 150 (=150) | conditional, one per cluster | 150 | 6.07 | 6 % | 5 % | 8.3 | 100 % |
| N-5 | half (=92) | marginal, all faults | 8992 | 9.97 | 48 % | 66 % | 6.4 | 100 % |
| N-5 | half (=92) | conditional, all faults | 8992 | 9.45 | 31 % | 48 % | 6.9 | 100 % |
| N-5 | half (=92) | marginal, one per cluster | 92 | 9.20 | 38 % | 43 % | 7.6 | 100 % |
| N-5 | half (=92) | conditional, one per cluster | 92 | 5.11 | 4 % | 4 % | 13.5 | 100 % |
| N-5 | 150 (=150) | marginal, all faults | 14751 | 10.10 | 53 % | 67 % | 6.4 | 100 % |
| N-5 | 150 (=150) | conditional, all faults | 14751 | 9.70 | 40 % | 54 % | 6.7 | 100 % |
| N-5 | 150 (=150) | marginal, one per cluster | 150 | 9.69 | 43 % | 49 % | 7.0 | 100 % |
| N-5 | 150 (=150) | conditional, one per cluster | 150 | 5.75 | 3 % | 4 % | 11.9 | 100 % |
| N-6 | half (=82) | marginal, all faults | 8592 | 9.83 | 46 % | 71 % | 6.7 | 100 % |
| N-6 | half (=82) | conditional, all faults | 8592 | 9.32 | 26 % | 54 % | 7.2 | 100 % |
| N-6 | half (=82) | marginal, one per cluster | 82 | 8.43 | 27 % | 35 % | 8.8 | 100 % |
| N-6 | half (=82) | conditional, one per cluster | 82 | 4.12 | 1 % | 2 % | 16.7 | 100 % |
| N-6 | 150 (=150) | marginal, all faults | 15749 | 9.91 | 48 % | 68 % | 6.7 | 100 % |
| N-6 | 150 (=150) | conditional, all faults | 15749 | 9.52 | 38 % | 55 % | 6.9 | 100 % |
| N-6 | 150 (=150) | marginal, one per cluster | 150 | 9.23 | 38 % | 48 % | 7.6 | 100 % |
| N-6 | 150 (=150) | conditional, one per cluster | 150 | 5.53 | 4 % | 6 % | 13.0 | 100 % |

