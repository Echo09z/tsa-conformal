"""Project the exported mean-pooled token embedding (seed 0, 128 dimensions, data/local/embed_main_s0.npz, written by
export_scores.py) onto its first 32 principal components for the repository: data/embed_pca32_s0.npz.

The first two components carry 97.5 % of the variance and the first 32 carry 99.7 %; KCP thresholds computed on the
projection and on the full embedding agree closely (see results/b3_summary.md). Rows follow data/scores_main.npz."""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
K = 32

z = np.load(ROOT / "data" / "local" / "embed_main_s0.npz")["z"].astype(np.float64)
mu = z.mean(0)
cov = np.cov((z - mu).T)
val, vec = np.linalg.eigh(cov)
val, vec = val[::-1], vec[:, ::-1]
proj = ((z - mu) @ vec[:, :K]).astype(np.float16)
np.savez_compressed(ROOT / "data" / f"embed_pca{K}_s0.npz", z=proj,
                    explained=np.cumsum(val)[:K] / val.sum(), run=np.array("seed 0"))
print(f"embed_pca{K}_s0.npz: {proj.shape}, cumulative explained variance {np.cumsum(val)[K - 1] / val.sum():.4f}")
