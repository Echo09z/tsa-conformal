# tsa-conformal

**A conformal trust layer for transient stability assessment: where its miss-rate guarantee holds, where it breaks under topology shift, and what restoring it costs.**

Yuankang Li · October 2026 · IEEE 39-bus system · builds on the trustworthiness layer of Alcántara & Chatzivasileiadis [1] and my set-based stability model [2]

## Summary

**Question.** [1] adds a conformal trust layer to a grid foundation model for N-k contingency screening. For stability screening, two questions follow. Can the layer bound the miss rate of unstable cases, rather than marginal coverage? Does that bound survive topologies the calibration has not seen?

**Observation.** A stability classifier is usually deployed with the threshold that misses at most 2 % of the unstable validation cases. That rule is class-conditional split conformal calibration on the unstable class. It bounds the miss rate directly, but only for cases exchangeable with the calibration set.

**Findings** (α = 2 %, five trained seeds, test layers with up to six line outages):

1. **The guarantee holds on training topologies and breaks under topology shift.** The model misses 1.97 % of unstable cases on the main layer, 5.4 % on held-out single-outage topologies, and 7.4–7.8 % at N-4 to N-6.
2. **Per-layer calibration (stratified conformal prediction, SCP in [1]) restores it, at a price.** Every layer is back at 2.0 % missed. However, false alarms rise to 17–24 % at N-4 to N-6, and the operator must know the outage order at the decision.
3. **Two-sided prediction sets turn false alarms into simulations.** Both error rates stay at 2 %, and 15–20 % of the N-4 to N-6 cases are referred to time-domain simulation. Referral concentrates on late instabilities: at N-4, 53 % of the unstable cases that lose synchronism more than 3 s after the decision are referred, against 0.9 % of those within 0.5 s.
4. **Kernel weighting (kernel-weighted conformal prediction, KCP in [1]) does not help on this model's embedding.** It reaches 1.1 % missed at N-4 with 56 % false alarms, while one lower threshold reaches the same miss rate with 22 %. The embedding nearly determines the score, so localizing on it conditions on the score itself.
5. **Missing PMUs are a cheaper shift than topology changes.** The missing PMUs are known at the decision, so masking the existing calibration cases restores 2.0 % without new simulation.

![Miss rate by layer](results/fig1_miss_by_layer.png)

## Results at α = 2 %

| evaluation layer | missed, main-layer calibration | missed, own-layer calibration | false alarms, own-layer calibration | referred to simulation, two-sided sets |
|---|---|---|---|---|
| main test | 1.97 | – | – | – |
| held-out N-1 topologies | 5.42 | – | – | – |
| N-2 | 4.35 | 2.06 | 4.9 | 3.1 |
| N-3 | 5.08 | 1.98 | 9.5 | 7.6 |
| N-4 | 7.41 | 2.03 | 17.1 | 14.9 |
| N-5 | 7.80 | 2.00 | 22.5 | 19.4 |
| N-6 | 7.72 | 2.01 | 23.6 | 20.0 |

All values are in %. Each is the mean over seeds of the mean over random calibration / test splits. There are five seeds (three for the unseen N-1 topologies) and 50 splits (20 for referrals). Standard deviations are in [`results/headline.md`](results/headline.md).

## What I did

- **Data.** Per-case predicted probabilities of the model in [2] from five trained seeds, with no retraining and no new simulation. `tools/` documents the export; it needs the model code, which is not included. The cases cover three groups:
  - the main layer: training topologies, new operating points;
  - five single-outage topologies left out of training;
  - 165–199 random topologies in each of the N-2 to N-6 layers.
- **Method.** Class-conditional split conformal calibration on the unstable class, with score 1 − p.
  - Faults on one operating point are correlated, so calibration / test splits are drawn by operating point or topology.
  - An exact variant with one case per operating point or topology is reported alongside.
  - The calibration code is model-agnostic (`src/`) and covered by 45 unit tests.
- **Experiments.** Each script regenerates its table in `results/`.

| | question | script | results |
|---|---|---|---|
| A1 | Does main-layer calibration hold on new topologies? | `experiments/a1_main_calibration.py` | [a1](results/a1_summary.md) |
| A2, B1 | Does calibration on each layer, or on N-2 only, restore it, and with how many topologies? | `experiments/a2_stratified.py` | [a2](results/a2_summary.md) |
| A3 | With two-sided sets, how many cases go to simulation, and which ones? | `experiments/a3_prediction_sets.py` | [a3](results/a3_summary.md) |
| A4 | What does a guarantee for one calibration, rather than on average, cost? | `experiments/a4_calibration_conditional.py` | [a4](results/a4_summary.md) |
| B2 | How do missing PMUs compare as a second shift? | `experiments/b2_missing_pmu.py` | [b2](results/b2_summary.md) |
| B3 | Does kernel-weighted calibration (KCP) on the model's embedding help? | `experiments/b3_kcp.py` | [b3](results/b3_summary.md) |

The full write-up is in [`docs/details.md`](docs/details.md).

## What this means for a trust layer

- **Bound the quantity the operator needs.** Calibrating on the unstable class bounds the miss rate itself. Conformal risk control with the miss indicator as the loss gives the same threshold [3].
- **"Unseen" has to mean outside the calibrated layers.** New topologies drawn from a calibrated layer keep the guarantee. A deeper layer breaks it: calibrating on N-2 only more than halves the excess but still misses 4.1–4.2 % at N-4 to N-6.
- **Calibration data per layer.** About five calibration topologies already put the average miss rate at α. A guarantee for a single calibration, P(miss rate > α) ≤ 5 %, is a different matter: at α = 2 % it needs at least 149 topologies of the layer and raises false alarms to 24–59 %. It is affordable only at a looser α.
- **Stratification needs the topology.** Assigning a case to its layer requires the outage order at the decision. The PMU-only model in [2] was designed to avoid that dependency.

## Limitations

- **Scope.** One test system, one simulator and one model architecture. The 118-bus system is not repeated.
- **Best case for per-layer calibration.** Topologies within a layer are random draws from one generator, so these results are a best case.
- **Correlated cases.** The main results use all faults of each calibration cluster and are therefore approximate. The exact one-per-cluster variant is reported alongside.
- **Referral not evaluated.** Referral assumes that time-domain simulation is available and returns before the instability develops.

## Reproduce

```bash
uv sync
uv run pytest                 # quantile edge cases, miss-rate bounds on synthetic data, set construction
./experiments/run_all.sh      # every table and figure in results/ (about ten minutes)
```

## References

[1] A. Alcántara and S. Chatzivasileiadis, "Trustworthiness layer for foundation models in power systems: Application to N-k contingency screening," arXiv:2602.07995, 2026.
[2] Y. Li, T. Xiao, S. Huang, and Y. Chen, "Transient stability assessment from generator-side PMU responses: A physically grounded set-based model and its applicability boundaries," under review at *IEEE Transactions on Power Systems*, 2026.
[3] A. N. Angelopoulos, S. Bates, A. Fisch, L. Lei, and T. Schuster, "Conformal risk control," in *Proc. ICLR*, 2024.
