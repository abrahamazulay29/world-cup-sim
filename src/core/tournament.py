#  src/core/tournament.py  -----------------------------------------------
from __future__ import annotations
import numpy as np
import pandas as pd
from .match_model import match_probabilities            # ← still the C++-backed Poisson

# -----------------------------------------------------------------------------
def _win_matrix(strength_df: pd.DataFrame) -> np.ndarray:
    """N×N matrix of P(A beats B) – computed **once** per Streamlit session."""
    # ``match_probabilities`` expects **log-strengths**.  ``calc_team_strength``
    # already provides these in the ``strength`` column whereas ``lambda`` is
    # the derived Poisson rate.  Using the latter was skewing favourites.
    strength = strength_df["strength"].to_numpy()
    N   = len(strength)
    P   = np.empty((N, N), dtype=np.float64)
    for i in range(N):
        for j in range(N):
            if i == j:
                P[i, j] = 0.5                       # never used
            else:
                P[i, j] = match_probabilities(strength[i], strength[j])["home"]
    return P

# -----------------------------------------------------------------------------
def simulate_many(strength_df: pd.DataFrame,
                  n_runs: int = 20_000,
                  seed: int | None = None) -> pd.DataFrame:
    """Fast MC using a *pre-computed* win-probability matrix."""
    rng = np.random.default_rng(seed)
    teams = strength_df["team"].tolist()
    idx   = np.arange(len(teams))
    P     = _win_matrix(strength_df)                # ← heavy once; then reused

    win_count = dict.fromkeys(teams, 0)

    for _ in range(n_runs):
        alive = idx.copy()

        # 1. naïve knock-out (64 → 1) – you can drop in your real bracket here
        while len(alive) > 1:
            rng.shuffle(alive)
            next_round = []
            for a, b in alive.reshape(-1, 2):
                if rng.random() < P[a, b]:
                    next_round.append(a)
                else:
                    next_round.append(b)
            alive = np.array(next_round, dtype=int)

        win_count[teams[int(alive[0])]] += 1

    probs = (pd.Series(win_count, name="champion_prob") / n_runs
             ).rename_axis("team").reset_index()
    return probs.sort_values("champion_prob", ascending=False)
