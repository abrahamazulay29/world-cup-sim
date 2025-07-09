#  src/core/strength.py  ------------------------------------------------------
from __future__ import annotations
import numpy as np
import pandas as pd

MU = np.log(1.35)               # ≈ World-Cup goals per team, per match


def calc_team_strength(df: pd.DataFrame, mu: float = MU) -> pd.DataFrame:
    """
    Convert bookmaker implied-championship probabilities into per-match
    Poisson scoring intensities.

    Returns columns
        team
        strength   – **log-strength**, geometric mean == 0
        implied_prob
        lambda     – Poisson rate  λ = exp( μ + strength )
    """
    # 1. average across the books
    out = (
        df.groupby("team", as_index=False)["implied_prob"]
          .mean()
          .sort_values("implied_prob", ascending=False)
    )

    # 2. centre *in log space*  →  geo-mean strength = 1
    log_s = np.log(out["implied_prob"])
    log_s -= log_s.mean()            # now mean(log_s) == 0
    out["strength"] = log_s          # ← KEEP **log** value

    # 3. per-match Poisson rate
    out["lambda"] = np.exp(mu + out["strength"])

    return out[["team", "strength", "implied_prob", "lambda"]]
