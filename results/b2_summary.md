# B2. Missing PMUs

Five seeds; random halves of the main-test operating points (and of the N-4 topologies for the own-layer rows); means over seeds x splits, %. Missing sets: k3_d0 = generators {0,4,7}, k3_d1 = generators {1,4,6}, k3_d2 = generators {2,7,8}, k5_d0 = generators {0,1,2,4,9}, k5_d1 = generators {2,3,4,6,9}, k5_d2 = generators {0,1,6,7,8}.

## alpha = 0.02: one-sided alarm threshold

| missing | main: miss, as deployed | main: miss, recalibrated | main: false alarm, recalibrated | N-4: miss, as deployed | N-4: miss, recalibrated on main | N-4: false alarm, recalibrated on main | N-4: miss, own layer | N-4: false alarm, own layer | validation recalibration: N-4 miss / false alarm |
|---|---|---|---|---|---|---|---|---|---|
| none | 2.03 | 2.03 | 1.60 | 7.44 | 7.44 | 6.32 | 2.02 | 17.26 | 7.14 / 6.59 |
| k3_d0 | 2.20 | 1.98 | 2.55 | 7.10 | 6.69 | 9.84 | 2.01 | 22.72 | 6.28 / 10.39 |
| k3_d1 | 2.73 | 2.01 | 2.73 | 8.38 | 7.13 | 8.87 | 2.03 | 22.24 | 7.40 / 8.55 |
| k3_d2 | 3.29 | 2.06 | 4.51 | 8.96 | 6.50 | 13.22 | 1.95 | 29.83 | 6.28 / 13.63 |
| k5_d0 | 15.37 | 2.01 | 28.95 | 29.89 | 6.14 | 48.71 | 1.96 | 71.17 | 6.55 / 46.97 |
| k5_d1 | 4.96 | 2.04 | 5.73 | 11.03 | 5.47 | 18.25 | 1.99 | 32.20 | 5.50 / 18.16 |
| k5_d2 | 4.34 | 1.98 | 8.66 | 9.76 | 6.08 | 20.65 | 1.96 | 40.45 | 6.28 / 20.09 |

## alpha = 0.02: two-sided sets, recalibrated under the same missing PMUs

miss = P(declared stable | unstable); false alarm = P({U} or {} | stable); refer = P({S,U}).

| missing | main: miss | main: false alarm | main: refer | N-4 (main calibration): miss | false alarm | refer | N-4 (own layer): miss | false alarm | refer |
|---|---|---|---|---|---|---|---|---|---|
| none | 1.53 | 1.96 | 0.00 | 6.35 | 7.44 | 0.00 | 2.02 | 2.02 | 14.91 |
| k3_d0 | 1.98 | 1.98 | 0.60 | 6.69 | 8.13 | 1.61 | 2.01 | 2.02 | 19.68 |
| k3_d1 | 2.01 | 1.95 | 0.83 | 7.13 | 6.70 | 2.13 | 2.03 | 2.03 | 19.20 |
| k3_d2 | 2.06 | 1.98 | 2.57 | 6.50 | 6.75 | 6.08 | 1.95 | 2.02 | 25.73 |
| k5_d0 | 2.01 | 1.98 | 24.96 | 6.14 | 7.24 | 36.76 | 1.96 | 2.02 | 61.39 |
| k5_d1 | 2.04 | 1.96 | 3.82 | 5.47 | 7.82 | 9.56 | 1.99 | 2.03 | 28.30 |
| k5_d2 | 1.98 | 1.98 | 6.74 | 6.08 | 6.97 | 12.32 | 1.96 | 2.02 | 34.44 |

## alpha = 0.05: one-sided alarm threshold

| missing | main: miss, as deployed | main: miss, recalibrated | main: false alarm, recalibrated | N-4: miss, as deployed | N-4: miss, recalibrated on main | N-4: false alarm, recalibrated on main | N-4: miss, own layer | N-4: false alarm, own layer | validation recalibration: N-4 miss / false alarm |
|---|---|---|---|---|---|---|---|---|---|
| none | 5.00 | 5.00 | 0.67 | 12.45 | 12.45 | 3.20 | 5.06 | 9.37 | 12.09 / 3.36 |
| k3_d0 | 6.23 | 5.00 | 1.12 | 12.98 | 11.38 | 5.26 | 5.05 | 12.79 | 10.97 / 5.53 |
| k3_d1 | 6.88 | 4.98 | 1.24 | 14.33 | 11.91 | 4.66 | 5.07 | 12.05 | 11.88 / 4.68 |
| k3_d2 | 8.18 | 5.04 | 1.90 | 16.00 | 11.97 | 6.54 | 4.97 | 16.66 | 11.47 / 6.93 |
| k5_d0 | 26.73 | 5.04 | 13.18 | 42.77 | 13.88 | 28.37 | 5.01 | 52.91 | 14.32 / 27.54 |
| k5_d1 | 11.20 | 5.05 | 2.51 | 20.36 | 11.19 | 9.46 | 5.04 | 19.50 | 11.76 / 8.96 |
| k5_d2 | 11.63 | 5.04 | 3.95 | 17.98 | 10.74 | 11.49 | 4.93 | 24.16 | 10.71 / 11.53 |

## alpha = 0.05: two-sided sets, recalibrated under the same missing PMUs

miss = P(declared stable | unstable); false alarm = P({U} or {} | stable); refer = P({S,U}).

| missing | main: miss | main: false alarm | main: refer | N-4 (main calibration): miss | false alarm | refer | N-4 (own layer): miss | false alarm | refer |
|---|---|---|---|---|---|---|---|---|---|
| none | 0.32 | 4.91 | 0.00 | 2.10 | 16.79 | 0.00 | 5.06 | 5.08 | 4.23 |
| k3_d0 | 0.75 | 4.92 | 0.00 | 3.46 | 16.50 | 0.00 | 5.05 | 5.07 | 7.41 |
| k3_d1 | 0.75 | 4.92 | 0.00 | 3.71 | 15.06 | 0.00 | 5.07 | 5.05 | 6.77 |
| k3_d2 | 1.80 | 4.96 | 0.00 | 5.89 | 14.35 | 0.00 | 4.97 | 5.06 | 10.91 |
| k5_d0 | 5.04 | 4.96 | 7.78 | 13.88 | 14.04 | 12.99 | 5.01 | 5.04 | 42.84 |
| k5_d1 | 2.48 | 4.93 | 0.00 | 6.38 | 16.18 | 0.00 | 5.04 | 5.09 | 13.76 |
| k5_d2 | 3.96 | 4.98 | 0.00 | 9.28 | 13.62 | 0.01 | 4.93 | 5.02 | 17.44 |

