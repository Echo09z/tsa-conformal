# A3. Two-sided prediction sets and referral to simulation

## alpha = 0.02 for both classes

Means over seeds x splits, %. miss = P(declared stable | unstable); false omission = P(unstable | declared stable); refer = P({S,U}); refer | U = P({S,U} | unstable); alarm | S = P({U} or {} | stable); empty = P({}).

| calibration | evaluation | miss | false omission | refer | refer, unstable | false alarm | empty | t_U | t_S |
|---|---|---|---|---|---|---|---|---|---|
| main | main test (other half) | 1.47 | 0.31 | 0.00 | 0.00 | 2.00 | 0.40 | 0.226 | 0.168 |
| main | held-out N-1 | 4.78 | 1.01 | 0.00 | 0.00 | 2.06 | 0.35 | 0.252 | 0.207 |
| main | N-2 | 3.54 | 0.98 | 0.00 | 0.00 | 3.25 | 0.61 | 0.226 | 0.168 |
| main | N-3 | 4.25 | 1.47 | 0.00 | 0.00 | 5.43 | 0.89 | 0.226 | 0.168 |
| main | N-4 | 6.29 | 2.85 | 0.00 | 0.00 | 7.52 | 1.15 | 0.226 | 0.168 |
| main | N-5 | 6.60 | 3.43 | 0.00 | 0.00 | 9.96 | 1.39 | 0.226 | 0.168 |
| main | N-6 | 6.57 | 3.80 | 0.00 | 0.00 | 10.61 | 1.43 | 0.226 | 0.168 |
| stratified | N-2 | 1.98 | 0.57 | 3.11 | 3.65 | 2.01 | 0.00 | 0.083 | 0.346 |
| stratified | N-3 | 2.04 | 0.74 | 7.64 | 8.24 | 1.99 | 0.00 | 0.068 | 0.610 |
| stratified | N-4 | 2.00 | 1.02 | 14.86 | 14.17 | 1.99 | 0.00 | 0.050 | 0.751 |
| stratified | N-5 | 2.02 | 1.24 | 19.41 | 17.43 | 2.00 | 0.00 | 0.050 | 0.829 |
| stratified | N-6 | 2.05 | 1.41 | 19.99 | 17.36 | 2.03 | 0.00 | 0.051 | 0.858 |

## alpha = 0.05 for both classes

Means over seeds x splits, %. miss = P(declared stable | unstable); false omission = P(unstable | declared stable); refer = P({S,U}); refer | U = P({S,U} | unstable); alarm | S = P({U} or {} | stable); empty = P({}).

| calibration | evaluation | miss | false omission | refer | refer, unstable | false alarm | empty | t_U | t_S |
|---|---|---|---|---|---|---|---|---|---|
| main | main test (other half) | 0.30 | 0.06 | 0.00 | 0.00 | 5.03 | 4.43 | 0.557 | 0.051 |
| main | held-out N-1 | 1.42 | 0.31 | 0.00 | 0.00 | 5.30 | 5.31 | 0.586 | 0.060 |
| main | N-2 | 0.89 | 0.26 | 0.00 | 0.00 | 7.88 | 6.79 | 0.557 | 0.051 |
| main | N-3 | 1.19 | 0.45 | 0.00 | 0.00 | 13.07 | 10.21 | 0.557 | 0.051 |
| main | N-4 | 2.05 | 1.05 | 0.00 | 0.00 | 16.98 | 12.77 | 0.557 | 0.051 |
| main | N-5 | 2.08 | 1.28 | 0.00 | 0.00 | 22.02 | 15.54 | 0.557 | 0.051 |
| main | N-6 | 1.96 | 1.36 | 0.00 | 0.00 | 23.67 | 16.02 | 0.557 | 0.051 |
| stratified | N-2 | 1.93 | 0.55 | 0.00 | 0.00 | 5.04 | 2.77 | 0.281 | 0.082 |
| stratified | N-3 | 4.62 | 1.58 | 0.02 | 0.02 | 4.95 | 0.43 | 0.221 | 0.192 |
| stratified | N-4 | 5.00 | 2.31 | 4.25 | 4.13 | 5.00 | 0.00 | 0.111 | 0.334 |
| stratified | N-5 | 5.08 | 2.73 | 7.33 | 7.01 | 4.98 | 0.00 | 0.107 | 0.491 |
| stratified | N-6 | 5.01 | 3.01 | 8.02 | 7.16 | 5.06 | 0.00 | 0.106 | 0.532 |

## Where the unstable samples end, alpha = 0.02

Unstable samples per draw (seed x split) in each lead-time bin, and the share (%) that is missed / referred / alarmed, pooled over draws; last column: share of voltage-first cases among the missed ones.

### main calibration, main test (other half)

| lead time | unstable per draw | missed | referred | alarm | voltage-first among missed |
|---|---|---|---|---|---|
| crossed in window | 900 | 0.0 | 0.0 | 100.0 | nan |
| 0-0.5 s | 1637 | 0.0 | 0.0 | 100.0 | 0 |
| 0.5-1 s | 281 | 0.7 | 0.0 | 99.3 | 5 |
| 1-3 s | 235 | 3.2 | 0.0 | 96.8 | 14 |
| > 3 s | 406 | 10.2 | 0.0 | 89.8 | 41 |

Voltage-first share: 35 % of the missed, 6 % of all unstable samples.

### main calibration, N-4

| lead time | unstable per draw | missed | referred | alarm | voltage-first among missed |
|---|---|---|---|---|---|
| crossed in window | 2807 | 0.0 | 0.0 | 100.0 | nan |
| 0-0.5 s | 8174 | 0.1 | 0.0 | 99.9 | 0 |
| 0.5-1 s | 1908 | 3.5 | 0.0 | 96.5 | 31 |
| 1-3 s | 1806 | 13.5 | 0.0 | 86.5 | 38 |
| > 3 s | 2840 | 27.8 | 0.0 | 72.2 | 54 |

Voltage-first share: 49 % of the missed, 14 % of all unstable samples.

### stratified calibration, N-4

| lead time | unstable per draw | missed | referred | alarm | voltage-first among missed |
|---|---|---|---|---|---|
| crossed in window | 1398 | 0.0 | 0.0 | 100.0 | nan |
| 0-0.5 s | 4083 | 0.0 | 0.9 | 99.1 | 0 |
| 0.5-1 s | 954 | 0.8 | 18.4 | 80.8 | 16 |
| 1-3 s | 895 | 5.0 | 31.0 | 63.9 | 42 |
| > 3 s | 1410 | 8.6 | 53.0 | 38.4 | 57 |

Voltage-first share: 51 % of the missed, 14 % of all unstable samples.

