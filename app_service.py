from __future__ import annotations

import math
import pandas as pd

DATA_PATH = "data/warframe_relic_rewards.csv"


def _clean_value(value):
    if value is None:
        return None

    try:
        if math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def load_relic_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def fetch_selected_relics_sync(selected_relic_names: list[str]) -> pd.DataFrame:
    df = load_relic_dataset()

    if not selected_relic_names:
        return df

    return df[df["relic_name"].isin(selected_relic_names)].copy()


def fetch_one_relic_details_sync(selected_relic_name: str) -> dict:
    df = load_relic_dataset()
    row_df = df[df["relic_name"] == selected_relic_name]

    if row_df.empty:
        return {}

    row = row_df.iloc[0]

    return {
        "relic_name": _clean_value(row["relic_name"]),
        "tier": _clean_value(row.get("tier")),
        "rewards": [
            (_clean_value(row.get("item_bronze1")), _clean_value(row.get("price_bronze1")), "bronze"),
            (_clean_value(row.get("item_bronze2")), _clean_value(row.get("price_bronze2")), "bronze"),
            (_clean_value(row.get("item_bronze3")), _clean_value(row.get("price_bronze3")), "bronze"),
            (_clean_value(row.get("item_argent1")), _clean_value(row.get("price_argent1")), "argent"),
            (_clean_value(row.get("item_argent2")), _clean_value(row.get("price_argent2")), "argent"),
            (_clean_value(row.get("item_gold1")), _clean_value(row.get("price_gold1")), "gold"),
        ],
        "ev_intact": _clean_value(row.get("ev_intact")),
        "ev_radiant": _clean_value(row.get("ev_radiant")),
    }