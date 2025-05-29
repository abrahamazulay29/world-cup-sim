"""Vig-stripping utilities."""

import numpy as np
import pandas as pd


def decimal_to_prob(decimal: float) -> float:
    return 1.0 / decimal


def strip_vig_h2h(row: pd.Series) -> pd.Series:
    """Rescale H2H implied probs so they sum to 1."""
    cols = ["home_odds", "away_odds", "draw_odds"]
    odds = [row[c] for c in cols if pd.notna(row[c])]
    probs = np.array([decimal_to_prob(o) for o in odds])
    if probs.sum() == 0:
        return row
    adj = probs / probs.sum()
    i = 0
    for c in cols:
        if pd.notna(row[c]):
            row[c.replace("_odds", "_prob")] = adj[i]
            i += 1
    return row


def strip_vig_outrights(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise outright odds per bookmaker so probabilities sum to 1."""
    out = []
    for _, grp in df.groupby("bookmaker"):
        probs = 1.0 / grp["decimal_odds"].to_numpy()
        adj = probs / probs.sum()
        tmp = grp.copy()
        tmp["implied_prob"] = adj
        out.append(tmp)
    return pd.concat(out, ignore_index=True)