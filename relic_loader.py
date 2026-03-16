import requests

RELIC_DATA_URL = (
    "https://raw.githubusercontent.com/WFCD/warframe-relic-data/"
    "development/data/Relics.json"
)


def load_relic_data(limit: int | None = None) -> list[dict]:
    response = requests.get(RELIC_DATA_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Exclure les Requiem
    data = [relic for relic in data if not relic["name"].startswith("Requiem")]

    if limit is not None:
        return data[:limit]

    return data


def extract_tier(name: str) -> str | None:
    for tier in ("Lith", "Meso", "Neo", "Axi"):
        if name.startswith(f"{tier} "):
            return tier
    return None