"""
Odds-API client.
Supports both:
  • Head-to-Head  (markets="h2h")
  • Outright-Winner (markets="outrights")
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

import pandas as pd
import requests
from pydantic import BaseModel, Field


class MarketH2H(BaseModel):
    bookmaker: str
    last_update: datetime
    home_odds: float = Field(alias="home_team")
    away_odds: float = Field(alias="away_team")
    draw_odds: float | None = None


class MatchOdds(BaseModel):
    id: str
    home_team: str
    away_team: str
    commence_time: datetime
    markets: List[MarketH2H]


class OddsAPIClient:
    """
    sport_key examples
      "soccer_fifa_world_cup_winner"   (outrights)
      "soccer_fifa_world_cup"          (h2h, closer to 2026)
      "soccer_usa_mls"                 (h2h now in-season)
    markets: "h2h" | "outrights"
    """

    def __init__(
        self,
        api_key: str | None = None,
        sport_key: str = "soccer_fifa_world_cup_winner",
        markets: str = "outrights",
        regions: str = "us",
        odds_format: str = "decimal",
    ) -> None:
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ODDS_API_KEY not set in env or passed to OddsAPIClient")

        self.base_url = (
            "https://api.the-odds-api.com/v4/sports/"
            f"{sport_key}/odds?regions={regions}&markets={markets}"
            f"&oddsFormat={odds_format}"
        )
        self.markets = markets

    # ───────────────────────────────────────────── fetch & flatten
    def fetch(self) -> list[dict]:
        resp = requests.get(f"{self.base_url}&apiKey={self.api_key}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def to_dataframe(self, raw: list[dict]) -> pd.DataFrame:
        """Return tidy DataFrame (h2h) or long DataFrame (outrights)."""
        rows: list[dict] = []
        for event in raw:
            for book in event["bookmakers"]:
                if self.markets == "h2h":
                    row = {
                        "match_id": event["id"],
                        "home_team": event["home_team"],
                        "away_team": event["away_team"],
                        "commence_time": event["commence_time"],
                        "bookmaker": book["title"],
                        "last_update": book["last_update"],
                    }
                    prices = {
                        o["name"]: float(o["price"])
                        for o in book["markets"][0]["outcomes"]
                    }
                    row.update(
                        {
                            "home_odds": prices.get(event["home_team"]),
                            "away_odds": prices.get(event["away_team"]),
                            "draw_odds": prices.get("Draw"),
                        }
                    )
                    rows.append(row)

                elif self.markets == "outrights":
                    # one row per team outcome
                    for outcome in book["markets"][0]["outcomes"]:
                        rows.append(
                            {
                                "event_id": event["id"],
                                "bookmaker": book["title"],
                                "last_update": book["last_update"],
                                "team": outcome["name"],
                                "decimal_odds": float(outcome["price"]),
                            }
                        )
        return pd.DataFrame(rows)
