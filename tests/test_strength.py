import pandas as pd
from src.core.strength import calc_team_strength


def test_strength_centered():
    df = pd.DataFrame(
        {"team": ["A", "B", "C"], "implied_prob": [0.4, 0.35, 0.25]}
    )
    out = calc_team_strength(df)
    # strengths should be zero-sum in log scale
    assert abs(out["strength"].mean()) < 1e-9
