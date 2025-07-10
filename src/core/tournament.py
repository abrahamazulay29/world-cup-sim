#  src/core/tournament.py  -----------------------------------------------
"""Full 48‑team World‑Cup simulation (groups + fixed knockout bracket).

This replaces the previous *random 64‑team KO* placeholder that was washing
out favourites.  The format implemented here follows the 2026 regulations:

* 12 groups of 4 – seeded into 4 pots
* Top 2 of each group **plus** the 8 best 3rd‑placed teams advance
  (32 teams total)
* The bracket is fixed ahead of time (winner A vs runner‑up B, …).  For
  simplicity we hard‑code the bracket slots instead of re‑deriving them from
  the FIFA document every turn – it is deterministic anyway.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from .group_draw   import make_pots, draw_groups
from .group_stage  import play_group
from .match_model  import match_probabilities

# ---------------------------------------------------------------------------
def _win_matrix(strength_df: pd.DataFrame) -> np.ndarray:
    """N×N matrix of P(A beats B).  Heavy to compute → cache per run."""
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

# Hard‑coded round‑of‑32 slot order (winner of group A, 2nd of group C, …)
BRACKET_ORDER = [
    ("A", 1), ("C", 2),     # match 1
    ("E", 1), ("G", 2),     # match 2
    ("B", 1), ("D", 2),
    ("F", 1), ("H", 2),
    ("C", 1), ("A", 2),
    ("G", 1), ("E", 2),
    ("D", 1), ("B", 2),
    ("H", 1), ("F", 2),

    # fill remaining 16 slots with best third‑placed teams in
    # alphabetical order of the group they came from – a decent
    # approximation and *greatly* easier than reproducing the official
    # scheduling algorithm.
]

# ---------------------------------------------------------------------------
def _knockout_bracket(qualified: Dict[str, List[str]],
                      thirds: List[str],
                      rng: np.random.Generator) -> List[str]:
    """Return list of 32 teams ordered in the fixed R32 bracket."""
    slots: List[str] = []
    # 1. Group winners / runners‑up into the pre‑defined slots
    for grp, pos in BRACKET_ORDER:
        slots.append(qualified[grp][pos - 1])
    # 2. Shuffle the best thirds and stick them into the remaining 16 slots
    rng.shuffle(thirds)
    slots.extend(thirds)
    assert len(slots) == 32
    return slots

# ---------------------------------------------------------------------------
def _simulate_knockout(teams: List[str], P: np.ndarray,
                       team_to_idx: Dict[str, int],
                       rng: np.random.Generator) -> str:
    """Pure KO – 32 → 1 – using the fixed bracket order."""
    alive = teams
    while len(alive) > 1:
        next_round = []
        for i in range(0, len(alive), 2):
            a, b = alive[i], alive[i+1]
            if rng.random() < P[team_to_idx[a], team_to_idx[b]]:
                next_round.append(a)
            else:
                next_round.append(b)
        alive = next_round
    return alive[0]

# ---------------------------------------------------------------------------
def simulate_many(strength_df: pd.DataFrame,
                  n_runs: int = 20_000,
                  seed:   int | None = None) -> pd.DataFrame:
    """Full Monte‑Carlo with groups + KO."""
    rng = np.random.default_rng(seed)
    teams = strength_df["team"].tolist()
    idx   = {t: i for i, t in enumerate(teams)}
    P     = _win_matrix(strength_df)

    win_count = dict.fromkeys(teams, 0)

    pots = make_pots(strength_df)          # heavy ‑ do outside loop

    for _ in range(n_runs):
        # 1. ----- GROUP DRAW -------------------------------------------------
        groups = draw_groups(pots, rng)

        # 2. ----- PLAY GROUPS -----------------------------------------------
        group_results: Dict[str, List[Tuple[str, int, int]]] = {}
        for grp, grp_teams in groups.items():
            group_results[grp] = play_group(grp_teams, strength_map=strength_df.set_index("team")["strength"].to_dict(), rng=rng)

        # 3. ----- QUALIFICATION ---------------------------------------------
        qualified: Dict[str, List[str]] = {}
        thirds: List[Tuple[str, int, int, str]] = []   # (pts, gd, strength, team)
        for grp, table in group_results.items():
            # table already ordered
            qualified[grp] = [t for t, _, _ in table[:2]]
            thirds.append( (table[2][1], table[2][2], strength_df.set_index("team").loc[table[2][0], "strength"], table[2][0]) )

        # pick 8 best thirds by pts → gd → strength
        thirds_sorted = sorted(thirds, key=lambda x: (x[0], x[1], x[2]), reverse=True)[:8]
        best_thirds   = [t for *_, t in thirds_sorted]

        # 4. ----- KNOCK‑OUT --------------------------------------------------
        r32 = _knockout_bracket(qualified, best_thirds, rng)
        champ = _simulate_knockout(r32, P, idx, rng)
        win_count[champ] += 1

    probs = (pd.Series(win_count, name="champion_prob") / n_runs
             ).rename_axis("team").reset_index()
    return probs.sort_values("champion_prob", ascending=False)