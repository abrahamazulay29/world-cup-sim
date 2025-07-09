import pandas as pd
import numpy as np
from src.core.strength import calc_team_strength


def test_strength_centered():
    df = pd.DataFrame(
        {"team": ["A", "B", "C"], "implied_prob": [0.4, 0.35, 0.25]}
    )
    out = calc_team_strength(df)
    # strengths are mean-centred in log space ⇒ arithmetic mean ≈ 0
    assert abs(out["strength"].mean()) < 1e-9
