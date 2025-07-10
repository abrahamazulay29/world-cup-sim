# World‑Cup 2026 Monte‑Carlo Simulator

*A market‑calibrated tournament engine that ingests live sportsbook odds, de‑vigs the board, and runs Poisson‑driven Monte‑Carlo simulations at C++ speed.*

---

## 🎯 Why this project matters

* **Market calibration** → identical workflow to pricing exotic derivatives: pull quotes ⇢ remove edge ⇢ map to model parameters.
* **Stochastic simulation** → large‑scale Monte‑Carlo with a C++17/pybind11 core, variance‑reduced sampling, and vectorised maths.
* **Risk decomposition** → break overall title equity into *path* & *match* components (scenario analysis / Greeks analogue).
* **Full‑stack delivery** → API ingestion, numerics, native‑code acceleration, Streamlit front‑end, Docker, and CI.

---

## 📦 Tech Stack & Libraries

| Layer           | Tools                                                                  |
| --------------- | ---------------------------------------------------------------------- |
| **Languages**   | Python 3.11 • C++17 (pybind11 module)                                  |
| **Numerics**    | NumPy • SciPy • Pandas • Numba (⚡)                                     |
| **Perf Engine** | `cpp/core.cpp` compiled to `libwc_sim.so` at install time              |
| **API**         | [The Odds API](https://theoddsapi.com/) for real‑time sportsbook lines |
| **Web UI**      | Streamlit                                                              |
| **DevOps**      | Docker • GitHub Actions CI                                             |

---

## 🚀 Quick Start

```bash
# 1 – clone & install (C++ builds automatically if a compiler is present)
$ git clone https://github.com/username/world‑cup‑sim.git
$ cd world‑cup‑sim
$ pip install -r requirements.txt
# 2 – add Odds API key
$ export ODDS_API_KEY="YOUR_KEY_HERE"
# 3 – launch UI
$ streamlit run app/Simulator.py
```

> **Tip:** add `WC_SIM_FAST=0` to force the pure‑Python path (helpful on Windows without MSVC).

---

## 🔍 How it Works

1. **Fetch outright prices** `src/data/odds_client.py` pulls Futures from The Odds API (JSON).
2. **Strip the vig** Convert American odds → raw implied *P*; divide by column sum to get “fair” probabilities.
3. **Translate into team strength** Center log‑odds, apply shrink factor `SCALE≈8`, yielding Gaussian‑like ratings.
4. **Group‑stage simulation** Round‑robin Poisson matches (xG derived from relative strength); tie‑break per FIFA rules.
5. **Knock‑out bracket** Fixed Round‑of‑32 bracket. Each match → Poisson goals, ET, then penalty shoot‑out model (C++ hot‑path).
6. **Monte‑Carlo engine** Vectorised tournament loop: chooses C++ backend (`libwc_sim`) if available, else Numba‑jit fallback.
7. **Streamlit UI** Renders probability tables, path heat‑maps, and exposes sliders for `SCALE` & sample size.

---

## 🔢 Example Output

| Team   | Vig‑free implied | Simulated title prob |
| ------ | ---------------- | -------------------- |
| Brazil | 17.2 %           | 16.8 %               |
| France | 14.1 %           | 13.7 %               |
| Spain  | 11.0 %           | 10.2 %               |

> *Numbers auto‑update with live odds.*

---

## 🛠️ Directory Layout

```
├── app/                 # Streamlit front‑end
├── cpp/                 # C++17 core (pybind11 wrapper)
│   └── core.cpp
├── src/
│   ├── data/            # Odds API client & vig‑removal
│   ├── models/          # Poisson, penalties, xG calibration
│   ├── tournament/      # Group draw & bracket logic
│   └── utils/           # Config, logging, helpers
├── tests/               # PyTest unit tests
└── Dockerfile           # Reproducible deploy
```

---

## 🗺️ Roadmap / Stretch Goals

* **Golden Boot / Ball simulations**
* **Parallel backend (Ray / Dask) for 1 M+ runs**
* **Automated daily scrape & write‑back to Postgres**
* **FastAPI micro‑service** for portfolio site embed

---

## 👤 Author

Abraham — Software Engineer & budding Quant.
