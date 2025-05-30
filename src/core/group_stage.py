"""
Round-robin engine for a 4-team World-Cup group.

For each fixture we draw actual goal counts from the Poisson rates
implied by the team-strength model, award points (3-1-0) and
update goal difference (GF − GA).  Returned list is sorted by
points, then goal-difference, then pre-tournament strength.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Tuple

from .match_model import expected_goals


def play_group(
    teams: List[str],
    strength_map: Dict[str, float],
    rng: np.random.Generator,
) -> List[Tuple[str, int, int]]:
    """Return [(team, points, gd)] ordered 1st→4th."""
    pts: Dict[str, int] = {t: 0 for t in teams}
    gd: Dict[str, int] = {t: 0 for t in teams}

    # double-loop over the six fixtures
    for i in range(4):
        for j in range(i + 1, 4):
            home, away = teams[i], teams[j]

            # draw scoreline from independent Poissons
            lam_h, lam_a = expected_goals(strength_map[home], strength_map[away])
            g_h = rng.poisson(lam_h)
            g_a = rng.poisson(lam_a)

            # points
            if g_h > g_a:
                pts[home] += 3
            elif g_h == g_a:
                pts[home] += 1
                pts[away] += 1
            else:
                pts[away] += 3

            # goal difference
            gd[home] += g_h - g_a
            gd[away] += g_a - g_h

    # tie-break ordering
    ordered = sorted(
        teams,
        key=lambda t: (pts[t], gd[t], strength_map[t]),
        reverse=True,
    )
    return [(t, pts[t], gd[t]) for t in ordered]
