# tsa-conformal

**Where a conformal miss-rate statement for transient stability assessment holds, where it fails under topology shift, and what restoring it costs.**

A transient stability classifier is usually deployed with a threshold chosen on held-out data so that at most 2 % of the unstable cases are missed. That rule is class-conditional split conformal prediction on the unstable class. Its miss-rate statement therefore holds for new cases that are exchangeable with the calibration cases, and only for those. This repository measures the statement on the IEEE 39-bus system with a set-based generator response model [2] and test layers with up to six line outages.

The statement holds on the main layer: 1.97 % missed at α = 2 %. It fails on single-line-outage topologies left out of training (5.4 %) and on the N-4 to N-6 layers (7.4–7.8 %). Two remedies, following Alcántara & Chatzivasileiadis [1], each restore it at a measurable price. Calibrating on each layer brings the miss rate back to 2.0 %, but it needs labelled cases from that layer and raises false alarms to 17–24 %. Adding two-sided prediction sets keeps both error rates at about 2 % instead, and sends 15–20 % of the N-4 to N-6 cases to time-domain simulation.

![Miss rate by layer](results/fig1_miss_by_layer.png)

## Motivation

Alcántara & Chatzivasileiadis [1] add a conformal "trustworthiness layer" to a power-system foundation model for N-k contingency screening. The setting here differs from theirs in two ways:

1. **What is controlled.** Their layer gives marginal coverage of a regression output. For stability screening, the quantity that matters is the miss rate of unstable cases, which are the rare class. Calibrating on the unstable class only bounds that miss rate directly. The same threshold also follows from conformal risk control with the miss indicator as the loss [4].
2. **Where the calibration data come from.** Their stratified calibration has calibration cases for every N-k order. Here the comparison is between a calibration that has seen the target layer and one that has not, and the question is how many topologies of a layer the calibration needs.

## The observation

The paper's threshold rule [2] is: *on the validation set, take the highest threshold whose miss rate is at most 2 %*. This is a split conformal threshold on the unstable class:

- nonconformity score s = 1 − p, where p is the predicted probability of instability;
- q̂ = the ⌈(n+1)(1−α)⌉-th smallest score of the n unstable calibration cases;
- an alarm is raised when 1 − p ≤ q̂.

The two thresholds differ by at most one order statistic (`tests/test_conformal.py`). Read as conformal calibration, the paper's own numbers say where the statement holds and where it does not:

| test set | miss rate at the paper's 2 % threshold |
|---|---|
| main test (training topologies, new operating points) | 1.9 % |
| five N-1 topologies left out of training | 4.9–5.6 % |
| N-4 (new topologies, new operating points) | 7.2 % |

## Data

`data/` holds per-case scores only:

- **`scores_main.npz`**: 363,300 cases, five trained seeds. Covers the validation set, the main test set and the N-2 to N-6 layers.
- **`scores_holdout.npz`**: 135,600 cases, three seeds. Comes from the same model trained without five N-1 topologies (outaged lines 3, 4, 5, 7, 32).

Each case has:

- the predicted probability of instability for every seed;
- the label (240° rotor-angle separation within 10 s);
- the operating point and topology ids;
- the clearing time;
- the 240° crossing time;
- the simulator criterion violated first;
- the pre-fault angle spread.

The fields are documented in `src/tsa_conformal/data.py`.

| set | cases | operating points | topologies | unstable |
|---|---|---|---|---|
| validation | 40,800 | 2,040 | 34 | 17.7 % |
| main test | 40,800 | 2,040 | 34 | 16.9 % |
| N-2 / N-3 / N-4 | 59,700 / 58,800 / 58,200 | 30 per topology | 199 / 196 / 194 | 21–30 % |
| N-5 / N-6 | 55,500 / 49,500 | 30 per topology | 185 / 165 | 33–35 % |

The simulated dataset, the simulator and the model code are not part of this repository. `tools/export_scores.py` documents how the scores were exported from the trained checkpoints, with nothing retrained and no new simulation. It recomputes every probability and checks it against the stored per-case predictions (largest difference 5 × 10⁻⁷) or against the stored miss rates for N-5, N-6 and the held-out topologies. Its log is in `data/export_log.txt`.

## Method

`src/tsa_conformal/` is model-agnostic: it takes probabilities and labels only.

- **Alarm threshold** (`alarm_threshold`): conformal quantile on unstable cases, as above. With fewer than ⌈1/α⌉ − 1 calibration cases (49 at α = 2 %) the quantile is infinite and every case raises an alarm.
- **Two-sided prediction sets** (`prediction_sets`): the stable class gets its own threshold, calibrated on stable cases with score s = p. Each set is read as an operating decision:
  - {S}: declared stable.
  - {U}: alarm.
  - {S,U}: referred to time-domain simulation.
  - ∅: treated as an alarm.
- **Exchangeability unit.** Cases cluster: each main-layer operating point has 20 faults, and each N-k topology has 30 operating points with 10 faults each. Calibration / test splits are therefore drawn by operating point on the main layer and by topology in the N-k layers, with 50 random splits per seed (20 for A3).
- **Two calibration variants.** Using all cases of the calibration clusters gives an approximate statement. The *strict* variant takes one random unstable case per calibration cluster; that calibration set is exchangeable with one random case of a new cluster, which makes the finite-sample statement exact. Both are reported.
- **Calibration-conditional threshold** (`alarm_threshold_conditional`). The statements above hold on average over the calibration draw. The conditional version [7] bounds instead the probability that a single calibration ends above α: P(miss rate > α) ≤ δ. It places the threshold at the (c+1)-th smallest calibration value, where c is the largest count with P(Binomial(n, α) ≤ c) ≤ δ. It needs n ≥ log δ / log(1 − α) exchangeable values: 149 at α = 2 %, δ = 5 %.
- **Uncertainty.** The spread over seeds and random splits is reported throughout. Miss rates on whole layers also get a topology-level bootstrap.

Every threshold, α and stratification is fixed on the calibration part; the test part is never used to choose anything.

## Results

All numbers below are generated by the scripts in `experiments/` and copied from `results/`. Headline table at α = 2 %: per seed, the mean over the random splits; then mean ± standard deviation over seeds (`results/headline.md`).

| evaluation set | miss, main-layer calibration | false alarm, main-layer calibration | miss, N-2 calibration | miss, own-layer calibration | false alarm, own-layer calibration | referred, two-sided, own layer |
|---|---|---|---|---|---|---|
| main test (other half) | 1.97 ± 0.07 | 1.62 ± 0.09 | – | – | – | – |
| held-out N-1 | 5.42 ± 0.35 | 1.78 ± 0.14 | – | – | – | – |
| N-2 | 4.35 ± 0.26 | 2.70 ± 0.08 | – | 2.06 ± 0.04 | 4.92 ± 0.19 | 3.11 ± 0.17 |
| N-3 | 5.08 ± 0.32 | 4.53 ± 0.15 | 2.51 ± 0.05 | 1.98 ± 0.06 | 9.53 ± 0.40 | 7.64 ± 0.20 |
| N-4 | 7.41 ± 0.47 | 6.36 ± 0.42 | 4.09 ± 0.14 | 2.03 ± 0.05 | 17.08 ± 0.51 | 14.86 ± 0.48 |
| N-5 | 7.80 ± 0.61 | 8.50 ± 0.62 | 4.18 ± 0.22 | 2.00 ± 0.04 | 22.52 ± 0.58 | 19.41 ± 0.35 |
| N-6 | 7.72 ± 0.51 | 9.03 ± 0.62 | 4.18 ± 0.17 | 2.01 ± 0.02 | 23.55 ± 0.68 | 19.99 ± 0.48 |

### A1. Main-layer calibration holds where it was calibrated and fails under topology shift

`experiments/a1_main_calibration.py` → `results/a1_summary.md`

- **Main test.** Calibrated on a random half of the main-test operating points, the miss rate on the other half is 0.96, 1.98, 4.99 and 9.99 % at α = 1, 2, 5 and 10 %.
- **Paper's validation set.** Calibrating on that set instead reproduces the paper: 1.87 % on the main test and 7.14 % on N-4.
- **Held-out N-1.** One unseen line outage is already enough to break the statement: 5.4 % at α = 2 %.
- **N-k layers.** The excess grows with the outage order (4.4 % at N-2, 7.4–7.8 % at N-4 to N-6) and with α (18.8 % at N-4 for α = 10 %).
- **False alarms.** These rise too, from 1.6 % on the main test to 9.0 % at N-6. This is consistent with the lower AUC on these layers in [2]: the scores become less separable, not merely shifted.
- **Strict variant.** One case per operating point gives the same picture with a wider spread.

### A2. Calibrating on each layer restores the miss rate, at a cost in false alarms and data

`experiments/a2_stratified.py` → `results/a2_summary.md`

- **Miss rate.** Calibrating each layer on half of its topologies brings the miss rate on the other half back to 2.0 % in every layer, with a seed standard deviation ≤ 0.06 points.
- **Price in false alarms.** False alarms rise to 4.9 % (N-2), 17.1 % (N-4) and 23.6 % (N-6), against 2.7, 6.4 and 9.0 % with main-layer calibration.
- **Number of topologies.** The mean miss rate sits at α already with 5 calibration topologies (about 450 unstable cases at N-4). The spread over random draws, however, depends on the number of topologies rather than the number of cases. At N-4 the 5th–95th percentile range is 0.7–3.9 % with 5 topologies and 1.4–2.6 % with 97.

  ![Data cost](results/fig2_data_cost.png)
- **One calibration exceeds α about half the time.** At every m, about half of the single calibrations end above α. The statement is marginal over the calibration draw; A4 measures what a statement about a single calibration costs.
- **Strict variant.** It needs at least 49 calibration topologies with an unstable case at α = 2 %. With the 82–100 topologies available per layer, the quantile falls on the smallest or second-smallest per-topology value. The result is a miss rate of 0.8–1.0 % with 33–49 % false alarms at N-3 to N-6. For the second limitation of [1], this means a clean finite-sample statement per layer needs on the order of 50 labelled topologies of that layer at α = 2 %.
- **B1: calibrating on N-2 only** (half of its topologies). This gives 2.5 % at N-3 and 4.1–4.2 % at N-4 to N-6, with 8–15 % false alarms. It halves the excess of main-layer calibration but still exceeds α beyond N-3.

### A3. Two-sided sets turn the false-alarm cost into referrals to simulation

`experiments/a3_prediction_sets.py` → `results/a3_summary.md`

- **Main-layer calibration.** The stable threshold (p ≤ 0.17) and the alarm threshold (p ≥ 0.23) do not overlap at α = 2 %. Nothing is referred; cases in the gap form empty sets and raise alarms. The miss rate at N-4 remains 6.3 %.
- **Own-layer calibration.** At N-4 the alarm threshold drops to 0.05 and the stable threshold rises to 0.75. Both error rates stay at 2.0 % in every layer. The price is referring 3.1 % (N-2), 7.6 % (N-3), 14.9 % (N-4), 19.4 % (N-5) and 20.0 % (N-6) of all cases to simulation. At α = 5 % the referrals are 0, 0, 4.3, 7.3 and 8.0 %.

  ![Referral](results/fig3_referral.png)
- **Which unstable cases are referred** (N-4, own-layer calibration, α = 2 %), grouped by lead time from the decision to the 240° crossing:

  | lead time | missed | referred | alarm |
  |---|---|---|---|
  | crossed within the input window | 0.0 % | 0.0 % | 100 % |
  | 0–0.5 s | 0.0 % | 0.9 % | 99.1 % |
  | 0.5–1 s | 0.8 % | 18.4 % | 80.8 % |
  | 1–3 s | 5.0 % | 31.0 % | 63.9 % |
  | > 3 s | 8.6 % | 53.0 % | 38.4 % |

  The referrals and the remaining misses are both late instabilities, and 51 % of the misses are voltage-first. This matches the boundary identified in [2]: late, partly voltage-driven instabilities. Whether a time-domain simulation finishes within that lead time is not evaluated here.

### A4. A single calibration, not the average over calibrations

`experiments/a4_calibration_conditional.py` → `results/a4_summary.md`

The calibration-conditional threshold is applied with δ = 5 %, using the same random splits as A1 and A2. Two quantities are reported: the share of single calibrations whose miss rate ends above α, and the price paid for lowering it (α = 2 %, five seeds × 50 splits):

| evaluation | calibration | values | P(miss > α) | miss | false alarm |
|---|---|---|---|---|---|
| main test | marginal, all faults of 1,020 points | 3,453 | 49 % | 2.00 % | 1.6 % |
| main test | conditional, all faults | 3,453 | 12 % | 1.63 % | 1.9 % |
| main test | conditional, one fault per point | 879 | 4 % | 1.21 % | 2.4 % |
| N-4 | marginal, all faults of 97 topologies | 8,766 | 49 % | 2.05 % | 17.1 % |
| N-4 | conditional, all faults of 97 topologies | 8,766 | 24 % | 1.80 % | 18.3 % |
| N-4 | conditional, one per topology, 97 topologies | 97 | – | 0 % | 100 % (no finite threshold) |
| N-4 | conditional, one per topology, 150 topologies | 150 | 6 % | 0.63 % | 52.3 % |

- **Main layer.** A single calibration can be made reliable at little cost. With one fault per operating point and the conditional threshold, 4 % of the calibrations end above α (5 % per operating point), and the false-alarm rate rises from 1.6 to 2.4 %.
- **Counting faults overstates the evidence.** Treating every fault as an independent calibration value gives a binomial margin that is too thin. With the conditional threshold, single calibrations still exceed α in 12 % of the draws on the main layer and in 18–36 % on the N-2 to N-6 layers. The faults of one operating point or topology are correlated, so the effective sample size is closer to the number of clusters.
- **Per N-k layer the reliable version is expensive.** At α = 2 % it needs at least 149 topologies of the layer, more than half of any layer here holds. With 150 calibration topologies, the share of single calibrations above α comes close to δ: 4–6 % for the per-topology miss rate, which is the quantity the statement refers to, and 3–8 % per case. The test part has only 15–49 topologies, so these shares carry about one point of evaluation noise. The threshold, however, lands on the smallest per-topology value: false alarms reach 24 % (N-2), 39 % (N-3), 52 % (N-4) and 58–59 % (N-5, N-6). At α = 5 % the same procedure costs 6–27 % false alarms, and at α = 10 % 2–13 %. For deep outage layers, a statement about one calibration is affordable only at a looser α.

## Reproduce

```bash
uv sync
uv run pytest                 # quantile edge cases, marginal and conditional miss-rate bounds on synthetic data, set construction
./experiments/run_all.sh      # all tables and figures in results/ (about one minute)
```

## Limitations

- **Scope.** One test system (IEEE 39-bus), one simulator and one model architecture (five seeds; three for the held-out N-1 model).
- **Best case for own-layer calibration.** Topologies within a layer are drawn at random by the same generator, so the per-layer calibration results are a best case. A real topology change is not a random draw from a known layer.
- **Correlated cases.** Faults on the same operating point or topology are correlated. The main results use all cases of the calibration clusters, so they are approximate; the strict variant is reported alongside.
- **Labelled cases needed.** Own-layer calibration needs labelled, that is simulated, cases from the layer. This repository measures how many are needed but not how to obtain them online.
- **Marginal statement.** A1–A3 are marginal over the calibration draw: a single calibration exceeds α about half the time. The conditional version (A4) is exact only with one fault per cluster. Per N-k layer at α = 2 % it needs at least 149 of the layer's 165–199 topologies, and then raises false alarms to 24–59 %.
- **Referral not evaluated.** Referral assumes that time-domain simulation is available and returns in time.

## Future work

- Kernel-weighted conformal prediction (the KCP of [1], v2) on the model's mean-pooled embedding, to adapt the threshold per case without stratifying by layer.
- Missing PMUs as a second kind of shift.
- Adaptive conformal inference [6] for online topology changes.
- Cluster-aware calibration that uses all faults of a cluster without counting them as independent, for example the pooling methods for two-layer hierarchical data [8].
- The 118-bus system.

## References

[1] A. Alcántara and S. Chatzivasileiadis, "Trustworthiness layer for foundation models in power systems: Application to N-k contingency screening," arXiv:2602.07995, 2026.
[2] Y. Li, T. Xiao, S. Huang, and Y. Chen, "Transient stability assessment from generator-side PMU responses: A physically grounded set-based model and its applicability boundaries," manuscript, 2026.
[3] V. Vovk, A. Gammerman, and G. Shafer, *Algorithmic Learning in a Random World*. Springer, 2005.
[4] A. N. Angelopoulos, S. Bates, A. Fisch, L. Lei, and T. Schuster, "Conformal risk control," in *Proc. ICLR*, 2024.
[5] J. Lei, M. G'Sell, A. Rinaldo, R. J. Tibshirani, and L. Wasserman, "Distribution-free predictive inference for regression," *J. Amer. Statist. Assoc.*, vol. 113, no. 523, pp. 1094–1111, 2018.
[6] I. Gibbs and E. Candès, "Adaptive conformal inference under distribution shift," in *Proc. NeurIPS*, 2021.
[7] V. Vovk, "Conditional validity of inductive conformal predictors," *Machine Learning*, 2013, doi:10.1007/s10994-013-5355-6.
[8] R. Dunn, L. Wasserman, and A. Ramdas, "Distribution-free prediction sets for two-layer hierarchical models," *J. Amer. Statist. Assoc.*, 2023, doi:10.1080/01621459.2022.2060112.
