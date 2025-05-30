from src.core.tournament import simulate_many
from src.core.strength import calc_team_strength
from src.core.vig import strip_vig_outrights
from src.data.odds_api import OddsAPIClient


def test_champ_prob_sums_to_one():
    raw = OddsAPIClient().to_dataframe(OddsAPIClient().fetch())
    df = strip_vig_outrights(raw)
    strengths = calc_team_strength(df)
    probs = simulate_many(strengths, n_runs=2000, seed=1)
    assert abs(probs["champion_prob"].sum() - 1.0) < 0.03  # small MC tolerance
