from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, List


def make_pots(strength_df: pd.DataFrame, pot_size: int = 12) -> List[pd.DataFrame]:
    df_sorted = strength_df.sort_values("strength", ascending=False).reset_index(drop=True)
    return [df_sorted.iloc[i * pot_size : (i + 1) * pot_size] for i in range(4)]


def draw_groups(pots: List[pd.DataFrame], rng: np.random.Generator) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {chr(ord("A") + i): [] for i in range(12)}
    for pot in pots:
        teams = pot["team"].to_list()
        rng.shuffle(teams)
        for i, t in enumerate(teams):
            groups[chr(ord("A") + i)].append(t)
    return groups
