"""Loading the exported per-sample scores (data/*.npz, written by tools/export_scores.py).

Every sample is one fault on one operating point of the IEEE 39-bus system. Fields:
  prob [runs, N]  predicted probability of instability, one row per trained seed
  threshold_val   per run, the paper's threshold (miss rate <= 2 % on the validation set)
  label           1 = unstable (240-degree rotor-angle separation within the 10-s horizon)
  set             0 val, 1 main test, 2..6 the N-2 .. N-6 layers, 10 held-out N-1 topologies (all their points),
                  11 their points of the standard test split
  layer           0 main layer (intact network and all N-1 topologies), k = N-k layer
  op, topo_key    operating point id, outaged lines of its topology ('' for the intact network)
  fault_dur       fault duration (clearing time after inception), s
  t240            time of the 240-degree crossing after inception, s (NaN for stable samples)
  first_violation simulator criterion violated first: 1 angle, 2 voltage, 3 frequency, 0 none
  delta0          pre-fault rotor-angle spread, degrees
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RESULTS = ROOT / "results"

SET_LABELS = {0: "val", 1: "test", 2: "N-2", 3: "N-3", 4: "N-4", 5: "N-5", 6: "N-6",
              10: "held-out N-1", 11: "held-out N-1 (test points)"}
NK_SETS = (2, 3, 4, 5, 6)
WINDOW_S = 0.20                      # input window after clearing; the decision is taken at its end
VOLTAGE_FIRST = 2


@dataclass
class Scores:
    prob: np.ndarray
    threshold_val: np.ndarray
    run: np.ndarray
    label: np.ndarray
    set: np.ndarray
    layer: np.ndarray
    op: np.ndarray
    topo: np.ndarray                  # integer topology id (index into topo_keys)
    topo_keys: np.ndarray
    fault_dur: np.ndarray
    t240: np.ndarray
    first_violation: np.ndarray
    delta0: np.ndarray
    held_lines: np.ndarray | None = None

    @property
    def n_runs(self) -> int:
        return self.prob.shape[0]

    def lead_time(self) -> np.ndarray:
        """Time from the decision (end of the post-clearing window) to the 240-degree crossing, s; NaN if stable."""
        clearing = np.rint(self.fault_dur / 0.01) * 0.01
        return self.t240 - (clearing + WINDOW_S)

    def voltage_first(self) -> np.ndarray:
        return self.first_violation == VOLTAGE_FIRST


def load(name: str = "scores_main") -> Scores:
    z = np.load(DATA / f"{name}.npz")
    keys, topo = np.unique(z["topo_key"], return_inverse=True)
    return Scores(prob=z["prob"], threshold_val=z["threshold_val"], run=z["run"], label=z["label"], set=z["set"],
                  layer=z["layer"], op=z["op"], topo=topo.astype(np.int32), topo_keys=keys, fault_dur=z["fault_dur"],
                  t240=z["t240"], first_violation=z["first_violation"], delta0=z["delta0"],
                  held_lines=z["held_lines"] if "held_lines" in z.files else None)
