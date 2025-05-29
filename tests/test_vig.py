import pandas as pd

from src.core.vig import decimal_to_prob, strip_vig_h2h, strip_vig_outrights


def test_decimal_to_prob():
    assert abs(decimal_to_prob(2.0) - 0.5) < 1e-9


def test_strip_vig_h2h():
    row = pd.Series({"home_odds": 1.8, "away_odds": 4.2, "draw_odds": 3.8})
    out = strip_vig_h2h(row.copy())
    probs = out[["home_prob", "away_prob", "draw_prob"]].sum()
    assert abs(probs - 1.0) < 1e-9


def test_strip_vig_outrights():
    df = pd.DataFrame(
        {
            "bookmaker": ["A", "A", "A"],
            "team": ["X", "Y", "Z"],
            "decimal_odds": [3.0, 4.0, 6.0],
        }
    )
    out = strip_vig_outrights(df)
    assert abs(out["implied_prob"].sum() - 1.0) < 1e-9
