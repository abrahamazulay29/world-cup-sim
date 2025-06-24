import pytest, time
import pandas as pd
from src.core._cxx import HAS_CXX, simulate_many_fast
from src.data.odds_api import OddsAPIClient
from src.core.vig import strip_vig_outrights
from src.core.strength import calc_team_strength

raw         = OddsAPIClient().to_dataframe(OddsAPIClient().fetch())
strength_df = calc_team_strength(strip_vig_outrights(raw))

@pytest.mark.skipif(not HAS_CXX, reason="C++ backend not built")
def test_cxx_prob_sums_to_one():
    probs = simulate_many_fast(strength_df, n_runs=5_000, seed=1)
    assert abs(probs["champion_prob"].sum() - 1.0) < 1e-6

@pytest.mark.skipif(not HAS_CXX, reason="C++ backend not built")
def test_cxx_speed():
    t0 = time.perf_counter()
    simulate_many_fast(strength_df, n_runs=20_000, seed=1)
    dt = time.perf_counter() - t0
    assert dt < 0.4, f"C++ core too slow ({dt:.2f}s)"
