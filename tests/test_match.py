from src.core.match_model import match_probabilities, expected_goals


def test_probs_sum_to_one():
    probs = match_probabilities(0.1, -0.2)
    assert abs(sum(probs.values()) - 1.0) < 1e-9


def test_expected_goals_sensible():
    lam_h, lam_a = expected_goals(0.0, 0.0)
    assert 0.5 < lam_h < 3.0 and 0.5 < lam_a < 3.0
