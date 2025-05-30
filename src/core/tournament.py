from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from .group_draw import make_pots, draw_groups
from .group_stage import play_group
from .match_model import match_probabilities


def rank_best_thirds(group_results: Dict[str, List[Tuple[str, int, int]]]) -> List[str]:
    thirds = [res[2] for res in group_results.values()]  # (team, pts, gd)
    thirds.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [t for t, _, _ in thirds[:8]]


def build_bracket(group_results: Dict[str, List[Tuple[str, int, int]]],
                  best_thirds: List[str],
                  rng: np.random.Generator) -> List[Tuple[str, str]]:
    winners = [res[1][0][0] for res in sorted(group_results.items())]
    runners = [res[1][1][0] for res in sorted(group_results.items())]
    rng.shuffle(best_thirds)

    pairings: List[Tuple[str, str]] = []
    # Pattern: W_A vs BT1, W_B vs R_D, W_C vs BT2, W_D vs R_B, etc.
    mapping = [
        (0, ("winner", 0), ("bt", 0)),
        (1, ("winner", 1), ("runner", 3)),
        (2, ("winner", 2), ("bt", 1)),
        (3, ("winner", 3), ("runner", 1)),
        (4, ("winner", 4), ("bt", 2)),
        (5, ("winner", 5), ("runner", 7)),
        (6, ("winner", 6), ("bt", 3)),
        (7, ("winner", 7), ("runner", 5)),
        (8, ("winner", 8), ("runner", 10)),
        (9, ("winner", 9), ("bt", 4)),
        (10, ("winner", 10), ("runner", 8)),
        (11, ("winner", 11), ("bt", 5)),
        (12, ("runner", 0), ("bt", 6)),
        (13, ("runner", 2), ("bt", 7)),
        (14, ("runner", 4), ("runner", 6)),
        (15, ("runner", 9), ("runner", 11)),
    ]

    idx = {"winner": winners, "runner": runners, "bt": best_thirds}
    for _, left, right in mapping:
        pairings.append((idx[left[0]][left[1]], idx[right[0]][right[1]]))

    return pairings


def knockout(pairings: List[Tuple[str, str]], strength: Dict[str, float], rng: np.random.Generator) -> str:
    while len(pairings) > 1:
        nxt = []
        for a, b in pairings:
            probs = match_probabilities(strength[a], strength[b])
            r = rng.random()
            if r < probs["home"]:
                nxt.append(a)
            elif r < probs["home"] + probs["draw"]:
                nxt.append(a if rng.random() < 0.5 else b)
            else:
                nxt.append(b)
        rng.shuffle(nxt)
        pairings = list(zip(nxt[::2], nxt[1::2]))
    a, b = pairings[0]
    return a if rng.random() < match_probabilities(strength[a], strength[b])["home"] else b


def simulate_tournament_once(strength_df: pd.DataFrame, rng: np.random.Generator) -> str:
    strength = dict(zip(strength_df["team"], strength_df["strength"]))
    groups = draw_groups(make_pots(strength_df), rng)

    group_results = {}
    for g, teams in groups.items():
        group_results[g] = play_group(teams, strength, rng)

    best_thirds = rank_best_thirds(group_results)
    pairings = build_bracket(group_results, best_thirds, rng)
    champion = knockout(pairings, strength, rng)
    return champion


def simulate_many(strength_df: pd.DataFrame, n_runs: int = 100_000, seed: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    winners = [simulate_tournament_once(strength_df, rng) for _ in range(n_runs)]
    vc = pd.Series(winners).value_counts().rename_axis("team").to_frame("champion_prob")
    vc["champion_prob"] /= n_runs
    return vc.reset_index()
