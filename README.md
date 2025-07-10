# World‑Cup 2026 Monte‑Carlo Simulator

*A market‑calibrated tournament engine that ingests live bookmaker odds, de‑vigs the board, and runs tens‑of‑thousands of Poisson‑driven match simulations in seconds.*

---

## 🎯 Why this project matters

* **Market calibration** → identical workflow to pricing exotic derivatives: pull quotes ⇢ remove edge ⇢ convert to model parameters.
* **Stochastic simulation** → large‑scale Monte‑Carlo with variance reduction, vectorised maths, and performance profiling.
* **Risk decomposition** → break overall title equity into *path* & *match* components (analogous to scenario analysis / Greeks).
* **Full‑stack delivery** → API ingestion, numerical core, Streamlit front‑end, Docker packaging & CI.

---

## 📦 Tech Stack & Libraries

| Layer        | Tools                                                                  |
| ------------ | ---------------------------------------------------------------------- |
| **Language** | Python 3.11                                                            |
| **Numerics** | NumPy • SciPy • Pandas • Numba (⚡)                                     |
| **API**      | [The Odds API](https://theoddsapi.com/) for real‑time sportsbook lines |
| **Web UI**   | Streamlit                                                              |
| **DevOps**   | Docker • GitHub Actions CI                                             |

---

## 🚀 Quick Start

```bash
# 1 – clone & install
$ git clone https://github.com/username/world‑cup‑sim.git
$ cd world‑cup‑sim
$ pip install -r requirements.txt
# 2 – add Odds API key
$ export ODDS_API_KEY="YOUR_KEY_HERE"
# 3 – launch UI
$ streamlit run app/Simulator.py
```

> **Note:** the app defaults to 20 000 simulations; bump `--runs` for tighter confidence intervals.

---

## 🔍 How it Works

1. **Fetch outright prices**
   `src/data/odds_client.py` pulls *all* 48‑team Futures from The Odds API (JSON).
2. **Strip the vig**
   Convert American odds → raw implied *P*; divide by column sum to get “fair” probabilities.
3. **Translate into team strength**
   Center log‑odds, apply a shrink factor `SCALE≈8`, yielding a Gaussian‑like rating.
4. **Group‑stage simulation**
   Round‑robin Poisson matches (xG derived from relative strength); table tiebreakers per FIFA rules.
5. **Knock‑out bracket**
   Fixed Round‑of‑32 bracket (per 2026 regulations). Each match → Poisson goals + time‑homogeneous ET, then penalty shoot‑out model.
6. **Monte‑Carlo engine**
   Vectorised tournament loop (Numba). Results aggregated into champion / QF / SF probabilities.
7. **Streamlit UI**
   Renders tables, path heat‑maps, histogram of sims, and exposes sliders for `SCALE` & sample size.

---

## 🔢 Example Output

| Team   | Fair implied odds | Simulated title prob |
| ------ | ----------------- | -------------------- |
| Brazil | 17.2 %            | 16.8 %               |
| France | 14.1 %            | 13.7 %               |
| Spain  | 11.0 %            | 10.2 %               |

> *Numbers shown are illustrative; they auto‑update with live odds.*

---

## 🛠️ Directory Layout

```
├── app/                 # Streamlit front‑end
├── src/
│   ├── data/            # Odds API client & vig‑removal
│   ├── models/          # Poisson, penalties, xG calibration
│   ├── tournament/      # Group draw & bracket logic
│   └── utils/           # Helpers, config, logging
├── tests/               # PyTest unit tests
└── Dockerfile           # Reproducible deploy
```

---

## 🗺️ Roadmap / Stretch Goals

* **Golden Boot / Ball simulations**
* **Parallel backend (Ray or Dask) for 1 M+ runs**
* **Automated daily scrape & write‑back to Postgres**
* **FastAPI micro‑service** for portfolio site embed.

---

## 👤 Author

Abraham — Software Engineer & budding Quant.
