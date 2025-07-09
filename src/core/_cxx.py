#  src/core/_cxx.py  ----------------------------------------------------------

from __future__ import annotations
import importlib, pandas as pd, numpy as np
from .tournament import simulate_many  # python fallback
from .match_model import match_probabilities

try:
    _cxx   = importlib.import_module("cxx_sim")
    HAS_CXX = True
except ModuleNotFoundError:
    HAS_CXX = False


def win_prob_fast(s_a: float, s_b: float) -> float:
    """Fast single-match win probability."""
    if HAS_CXX:
        return _cxx.win_prob(s_a, s_b)
    return match_probabilities(s_a, s_b)["home"]


def simulate_many_fast(strength_df: pd.DataFrame,
                       n_runs: int = 20_000,
                       seed: int | None = None) -> pd.DataFrame:
    """Run the tournament Monte-Carlo using the C++ backend when available."""
    if HAS_CXX:
        teams      = strength_df["team"].tolist()
        strengths  = strength_df["strength"].to_numpy(dtype=float).tolist()
        probs_dict = _cxx.simulate_many(teams, strengths,
                                        n_runs=n_runs,
                                        seed=0 if seed is None else seed)
        return (pd.Series(probs_dict, name="champion_prob")
                .rename_axis("team")
                .reset_index()
                .sort_values("champion_prob", ascending=False))
    return simulate_many(strength_df, n_runs=n_runs, seed=seed)
