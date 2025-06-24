"""
_cxx.py tries to import the compiled extension;
falls back to slow Python functions transparently.
"""
from __future__ import annotations
import importlib
import numpy as np
import pandas as pd

try:
    _cxx = importlib.import_module("cxx_sim")
    HAS_CXX = True
except ModuleNotFoundError:
    HAS_CXX = False

from .tournament import simulate_many as py_simulate_many  # noqa: E402


def simulate_many_fast(strength_df: pd.DataFrame,
                       n_runs: int = 20_000,
                       seed: int | None = None) -> pd.DataFrame:
    """Return champion probabilities using the best available backend."""
    if HAS_CXX:
        teams   = strength_df["team"].tolist()
        lambdas = strength_df["lambda"].to_numpy(dtype=float).tolist()
        probs   = _cxx.simulate_many(teams, lambdas,
                                     n_runs=n_runs,
                                     seed=0 if seed is None else seed)
        return (pd.Series(probs, name="champion_prob")
                .rename_axis("team")
                .reset_index()
                .sort_values("champion_prob", ascending=False))
    # fallback to Python
    return py_simulate_many(strength_df, n_runs=n_runs, seed=seed)
