#!/usr/bin/env python
"""
Fetch latest odds and persist as Parquet.

Usage examples:
  python src/data/fetch_odds.py               # WC winner outrights
  python src/data/fetch_odds.py --sport soccer_usa_mls --markets h2h
"""

import pathlib
from datetime import datetime

import typer
from dotenv import load_dotenv

from src.data.odds_api import OddsAPIClient
from src.core.vig import strip_vig_h2h, strip_vig_outrights

app = typer.Typer()
load_dotenv()


@app.command()
def main(
    sport: str = typer.Option("soccer_fifa_world_cup_winner"),
    markets: str = typer.Option("outrights"),
    output_dir: pathlib.Path = typer.Option(pathlib.Path("data/raw")),
):
    output_dir.mkdir(parents=True, exist_ok=True)
    client = OddsAPIClient(sport_key=sport, markets=markets)
    raw = client.fetch()
    df = client.to_dataframe(raw)

    if markets == "h2h":
        df = df.apply(strip_vig_h2h, axis=1)
    elif markets == "outrights":
        df = strip_vig_outrights(df)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = output_dir / f"odds_{sport}_{markets}_{ts}.parquet"
    df.to_parquet(out_path, index=False)
    typer.echo(f"Saved {len(df)} rows → {out_path}")


if __name__ == "__main__":
    app()
