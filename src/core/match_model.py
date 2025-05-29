"""
Single-match Poisson model using team strengths.
λ_home = exp(μ + s_home − s_away)
λ_away = exp(μ + s_away − s_home)
We pick μ so the expected goals per team ≈ 1.35 (world-cup average).
"""

from __future__ import annotations
import numpy as np
from scipy.stats import poisson


MU = np.log(1.35)  # baseline log-rate


def expected_goals(s_home: float, s_away: float) -> tuple[float, float]:
    lam_home = np.exp(MU + s_home - s_away)
    lam_away = np.exp(MU + s_away - s_home)
    return lam_home, lam_away


def match_probabilities(s_home: float, s_away: float, max_goals: int = 8) -> dict:
    """
    Returns dict {home_win, draw, away_win} using independent Poissons truncated at max_goals.
    """
    lam_h, lam_a = expected_goals(s_home, s_away)

    probs = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for i in range(max_goals + 1):
        p_i = poisson.pmf(i, lam_h)
        for j in range(max_goals + 1):
            p_j = poisson.pmf(j, lam_a)
            if i > j:
                probs["home"] += p_i * p_j
            elif i == j:
                probs["draw"] += p_i * p_j
            else:
                probs["away"] += p_i * p_j
    # normalise residual tail mass (tiny)
    total = sum(probs.values())
    for k in probs:
        probs[k] /= total
    return probs
