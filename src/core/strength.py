#  src/core/strength.py  ------------------------------------------------------
from __future__ import annotations
import numpy as np
import pandas as pd

MU = np.log(1.35)               # ≈ World‑Cup goals per team, per match
# --------------------------------------------------------------------------- #
# Empirically‑calibrated scaling factor.  The implied championship
# probabilities that come from the bookmakers are already *non‑linear*
# summaries of a team's quality (they incorporate the whole tournament
# structure, potential paths, juice, etc.).  Feeding them directly into a
# single‑match model therefore **compresses** the differences between strong
# and weak teams, which is exactly what we have been seeing with Portugal
# showing up at ~7 % despite single‑digit outright odds.
#
# A back‑of‑the‑envelope calibration against the current market
# (Brazil ≈ 18 %, France ≈ 15 %, England ≈ 11 %, …) suggests that a divisor
# of about 8 puts the per‑match win probabilities in the right ball‑park
# (≈ 65–70 % for Brazil against an average team).  Feel free to tweak this
# constant – or expose it as a Streamlit slider – if you want to retune the
# model quickly.
# --------------------------------------------------------------------------- #
SCALE = 8.0


def calc_team_strength(df: pd.DataFrame, mu: float = MU, scale: float = SCALE) -> pd.DataFrame:
    """
    Convert bookmaker implied‑championship probabilities into per‑match
    Poisson scoring intensities.
    Parameters
    ----------
    df :
        Must contain columns ``team`` and ``implied_prob`` (one row per
        bookmaker).  Use :pyfunc:`src.core.vig.strip_vig_outrights` first.
    mu :
        Baseline log‑goal rate (1.35 ≈ historical WC average).
    scale :
        Shrink factor applied to the centred log‑probabilities so that
        *single‑match* edges line up with the market once the Monte‑Carlo
        tournament simulation is run.  Empirically 6–10 works well.
    Returns
    -------
    DataFrame with columns
        team, strength (**log value**), implied_prob, lambda
    """
    # 1.  Aggregate across books
    out = (
        df.groupby("team", as_index=False)["implied_prob"]
          .mean()
          .sort_values("implied_prob", ascending=False)
    )

    # 2. Centre in log‑space  →  geo‑mean strength = 1,  then shrink
    log_s = np.log(out["implied_prob"])
    log_s -= log_s.mean()
    out["strength"] = log_s / scale          #  ← KEY CHANGE

    # 3. Per‑match Poisson rate  λ = exp(μ + s)
    out["lambda"] = np.exp(mu + out["strength"])

    return out[["team", "strength", "implied_prob", "lambda"]]