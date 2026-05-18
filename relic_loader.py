from __future__ import annotations

import json
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent
LOCAL_RELIC_DATA_PATH = BASE_DIR / "data" / "Relics.json"

RELIC_DATA_URL = (
    "https://raw.githubusercontent.com/WFCD/warframe-relic-data/"
    "development/data/Relics.json"
)


def load_relic_data() -> list[dict]:
    if LOCAL_RELIC_DATA_PATH.exists():
        with LOCAL_RELIC_DATA_PATH.open(encoding="utf-8") as file:
            data = json.load(file)
    else:
        response = requests.get(RELIC_DATA_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

    return [relic for relic in data if not relic["name"].startswith("Requiem")]


def extract_tier(name: str) -> str | None:
    for tier in ("Lith", "Meso", "Neo", "Axi"):
        if name.startswith(f"{tier} "):
            return tier
    return None


def available_relic_names() -> list[str]:
    return [f"{relic['name']} Relic" for relic in load_relic_data()]
