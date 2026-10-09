"""Figures and the headline table from the A1-A3 result files (run a1, a2, a3 first).

Outputs: results/fig1_miss_by_layer.png, results/fig2_data_cost.png, results/fig3_referral.png, results/headline.md
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from tsa_conformal import data as D  # noqa: E402

ALPHA = 0.02
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]                  # categorical slots 1-3
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]          # sequential blue, ordinal steps 250 / 400 / 550 / 700
LAYERS = ["N-2", "N-3", "N-4", "N-5", "N-6"]

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": TEXT, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "legend.frameon": False})


def band(v: pd.Series) -> tuple[float, float, float]:
    return 100 * v.mean(), 100 * v.quantile(0.05), 100 * v.quantile(0.95)


def target_line(ax, text: str, x: float = 1.0, ha: str = "right") -> None:
    """Dashed line at the target alpha, labelled at axes fraction x."""
    ax.axhline(100 * ALPHA, color=MUTED, lw=1, ls=(0, (4, 3)))
    ax.text(x, 100 * ALPHA, text, transform=ax.get_yaxis_transform(), ha=ha, va="bottom", color=MUTED, fontsize=8)


def fig1(a1: pd.DataFrame, a2: pd.DataFrame) -> None:
    sets = ["main test", "held-out N-1"] + LAYERS
    a1 = a1[(a1.alpha == ALPHA) & (a1.cal == "test-half")]
    a2 = a2[(a2.alpha == ALPHA) & (a2.m == "half") & (a2.variant == "all samples")]
    series = {
        "main layer": {s: band(a1[a1["eval"] == ("main test (other half)" if s == "main test" else s)].miss) for s in sets},
        "N-2 only": {s: band(a2[(a2.cal_layer == "N-2") & (a2["eval"] == s)].miss) for s in LAYERS[1:]},
        "own layer (stratified)": {s: band(a2[(a2.cal_layer == s) & (a2["eval"] == s)].miss) for s in LAYERS},
    }
    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    x = np.arange(len(sets))
    for k, (name, vals) in enumerate(series.items()):
        xs = [x[sets.index(s)] + (k - 1) * 0.22 for s in vals]
        mean, lo, hi = (np.array([v[i] for v in vals.values()]) for i in range(3))
        ax.vlines(xs, lo, hi, color=SERIES[k], lw=2)
        ax.plot(xs, mean, "o", ms=6, color=SERIES[k], mec=SURFACE, mew=1.5, label=f"calibrated on {name}")
    target_line(ax, "alpha = 2 %", x=0.145, ha="center")
    ax.set_xticks(x, sets)
    ax.set_ylabel("miss rate of unstable cases (%)")
    ax.set_ylim(0, None)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Miss rate at alpha = 2 %: mean and 5th-95th percentile over seeds x splits", loc="left",
                 color=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(D.RESULTS / "fig1_miss_by_layer.png", dpi=200)
    plt.close(fig)


def fig2(a2: pd.DataFrame) -> None:
    d = a2[(a2.alpha == ALPHA) & (a2.cal_layer == "N-4") & (a2["eval"] == "N-4") & (a2.variant == "all samples")]
    g = d.groupby("n_cal_topologies").miss
    m = np.array(sorted(d.n_cal_topologies.unique()))
    mean, lo, hi = (100 * g.mean()).loc[m], (100 * g.quantile(0.05)).loc[m], (100 * g.quantile(0.95)).loc[m]
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.fill_between(m, lo, hi, color=SERIES[0], alpha=0.18, lw=0)
    ax.plot(m, mean, "-o", color=SERIES[0], lw=2, ms=6, mec=SURFACE, mew=1.5)
    ax.text(m[0], hi.iloc[0], "  5th-95th percentile", color=MUTED, fontsize=8, va="bottom")
    ax.axvline(49, color=MUTED, lw=0.8, ls=":")
    ax.text(49, ax.get_ylim()[1] * 0.98, " strict variant\n finite from 49", color=MUTED, fontsize=8, va="top")
    target_line(ax, "alpha = 2 %")
    ax.set_xscale("log")
    ax.set_xticks(m, [str(v) for v in m])
    ax.minorticks_off()
    ax.set_xlabel("calibration topologies drawn from N-4")
    ax.set_ylabel("miss rate on the other N-4 topologies (%)")
    ax.set_ylim(0, None)
    ax.set_title("N-4, stratified calibration, alpha = 2 %", loc="left", color=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(D.RESULTS / "fig2_data_cost.png", dpi=200)
    plt.close(fig)


def fig3(a3: pd.DataFrame) -> None:
    d = a3[a3.cal == "stratified"]
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    x = np.arange(len(LAYERS))
    for k, a in enumerate(sorted(d.alpha.unique())):
        y = [100 * d[(d.alpha == a) & (d["eval"] == s)].refer.mean() for s in LAYERS]
        ax.plot(x, y, "-o", color=RAMP[k], lw=2, ms=6, mec=SURFACE, mew=1.5, label=f"alpha = {100 * a:.0f} %")
        ax.text(x[-1] + 0.12, y[-1], f"{100 * a:.0f} %", color=MUTED, fontsize=8, va="center")
    ax.set_xticks(x, LAYERS)
    ax.set_xlim(-0.3, len(LAYERS) - 0.4)
    ax.set_ylabel("cases referred to simulation (%)")
    ax.set_ylim(0, None)
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Two-sided sets, stratified calibration", loc="left", color=TEXT, fontsize=9)
    fig.tight_layout()
    fig.savefig(D.RESULTS / "fig3_referral.png", dpi=200)
    plt.close(fig)


def headline(a1: pd.DataFrame, a2: pd.DataFrame, a3: pd.DataFrame) -> str:
    """alpha = 0.02; per seed the mean over splits, then mean +- standard deviation over seeds."""
    def seed_stats(df: pd.DataFrame, col: str) -> str:
        v = 100 * df.groupby("seed")[col].mean()
        return f"{v.mean():.2f} ± {v.std():.2f}"

    a1 = a1[a1.alpha == ALPHA]
    a2 = a2[(a2.alpha == ALPHA) & (a2.m == "half") & (a2.variant == "all samples")]
    a3 = a3[a3.alpha == ALPHA]
    out = ["# Headline numbers, alpha = 0.02", "",
           "Per seed: mean over random calibration / test splits; then mean ± standard deviation over the seeds "
           "(five for the proposed model, three for the model trained without five N-1 topologies). %.", "",
           "| evaluation set | miss, main-layer calibration | false alarm, main-layer calibration | "
           "miss, N-2 calibration | miss, stratified | false alarm, stratified | referred, two-sided stratified |",
           "|---|---|---|---|---|---|---|"]
    for s in ["main test (other half)", "held-out N-1"] + LAYERS:
        m1 = a1[(a1.cal == "test-half") & (a1["eval"] == s)]
        b1 = a2[(a2.cal_layer == "N-2") & (a2["eval"] == s)] if s in LAYERS[1:] else None
        st = a2[(a2.cal_layer == s) & (a2["eval"] == s)] if s in LAYERS else None
        r3 = a3[(a3.cal == "stratified") & (a3["eval"] == s)] if s in LAYERS else None
        cell = lambda df, c: seed_stats(df, c) if df is not None and len(df) else "–"  # noqa: E731
        out.append(f"| {s} | {cell(m1, 'miss')} | {cell(m1, 'false_alarm')} | {cell(b1, 'miss')} | "
                   f"{cell(st, 'miss')} | {cell(st, 'false_alarm')} | {cell(r3, 'refer')} |")
    return "\n".join(out) + "\n"


def main() -> None:
    a1 = pd.read_csv(D.RESULTS / "a1_main_calibration.csv")
    a2 = pd.read_csv(D.RESULTS / "a2_stratified.csv")
    a3 = pd.read_csv(D.RESULTS / "a3_prediction_sets.csv")
    fig1(a1, a2)
    fig2(a2)
    fig3(a3)
    (D.RESULTS / "headline.md").write_text(headline(a1, a2, a3))
    print((D.RESULTS / "headline.md").read_text())


if __name__ == "__main__":
    main()
