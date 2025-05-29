"""
Turn bookmaker outright-implied probabilities into log-strength parameters.
We’ll treat strength on a log-odds scale so that:
    strength_i = ln(p_i) - ln(p_ref)
where p_ref is the geometric mean of all probs.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pandas import DataFrame


def calc_team_strength(outright_df: pd.DataFrame) -> pd.DataFrame:
    """
    Expects columns: ['team', 'implied_prob'] for one bookmaker (vig-stripped).
    Returns DataFrame with added 'strength' column.
    """
    # aggregate same-team rows (we keep mean prob over bookmakers)
    grp = outright_df.groupby("team", as_index=False)["implied_prob"].mean()

    # geometric mean as neutral reference
    p_ref = np.exp(np.log(grp["implied_prob"]).mean())

    grp["strength"] = np.log(grp["implied_prob"] / p_ref)
    return DataFrame(grp.loc[:, ["team", "strength", "implied_prob"]])
