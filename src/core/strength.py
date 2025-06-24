from __future__ import annotations
import pandas as pd
import numpy as np

_BASE_LAMBDA = 1.45   # avg goals per team per match (Europe 2022-24)

def calc_team_strength(df: pd.DataFrame, base_lambda: float = _BASE_LAMBDA) -> pd.DataFrame:
    """
    Turn implied championship probabilities into a per-match scoring intensity.

    Returns columns:
        team, strength (unit-norm), implied_prob, lambda
    """
    out = (
        df.groupby("team", as_index=False)["implied_prob"]
          .mean()                             # bookmaker average
          .sort_values("implied_prob", ascending=False)
    )
    log_s = np.log(out["implied_prob"])
    log_s -= log_s.mean()
    out["strength"] = np.exp(log_s)

    # expected goals λ = base × strength
    out["lambda"] = base_lambda * out["strength"]

    return out[["team", "strength", "implied_prob", "lambda"]]
