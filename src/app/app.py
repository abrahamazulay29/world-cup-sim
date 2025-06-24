"""
World-Cup 2026 Monte-Carlo dashboard
Run locally:  streamlit run src/app/app.py
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.data.odds_api import OddsAPIClient
from src.core.vig import strip_vig_outrights
from src.core.strength import calc_team_strength
from src.core._cxx import simulate_many_fast as simulate_many, HAS_CXX  # ← NEW

# ── page setup ─────────────────────────────────────────────────────────────
st.set_page_config("WC-26 Simulator", layout="wide")
st.title("⚽ FIFA World Cup 2026 — Monte-Carlo Simulator")

# ── sidebar controls ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Simulation settings")
    n_runs = st.slider("Monte-Carlo paths", 1_000, 100_000, 20_000, step=1_000)
    seed   = st.number_input("Random seed", value=42, step=1)
    run_btn = st.button("🔄 Run simulation")

    # backend info
    st.caption(
        "Backend:  "
        + ("🟢 **C++ (pybind11)**" if HAS_CXX else "🟡 Python")
    )

# ── load bookmaker odds once per session ───────────────────────────────────
@st.cache_data(show_spinner=False)
def load_strength_df() -> pd.DataFrame:
    raw = OddsAPIClient(
        sport_key="soccer_fifa_world_cup_winner",
        markets="outrights",
    ).to_dataframe(OddsAPIClient().fetch())
    return calc_team_strength(strip_vig_outrights(raw))

strength_df = load_strength_df()

# ── run Monte-Carlo when clicked ───────────────────────────────────────────
if run_btn:
    st.toast("Running simulation…", icon="⏳")
    probs = simulate_many(strength_df, n_runs=int(n_runs), seed=int(seed))
    st.success("Done!", icon="✅")

    # champion-probability table
    st.subheader("Champion probabilities")
    st.dataframe(
        probs.sort_values("champion_prob", ascending=False)
             .style.format({"champion_prob": "{:.2%}"})
    )

    # top-12 bar chart
    top = probs.nlargest(12, "champion_prob").sort_values("champion_prob")
    fig = px.bar(
        top,
        x="champion_prob",
        y="team",
        orientation="h",
        labels={"champion_prob": "Win %", "team": ""},
        title="Top-12 favourites",
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Adjust parameters in the sidebar and click **Run simulation**.")
