from __future__ import annotations

import requests


HEADERS = {
    "Platform": "pc",
    "Language": "en",
    "Accept": "application/json",
    "User-Agent": "warframe-relic-builder/1.0",
}

ORDERS_URL = "https://api.warframe.market/v1/items/{}/orders"
STATS_URL = "https://api.warframe.market/v1/items/{}/statistics"


def best_sell_price_from_api(slug: str) -> float | None:
    try:
        response = requests.get(ORDERS_URL.format(slug), headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    orders = data.get("payload", {}).get("orders", [])
    if not orders:
        return None

    ingame_prices: list[float] = []
    online_prices: list[float] = []
    all_prices: list[float] = []

    for order in orders:
        if order.get("order_type") != "sell":
            continue

        if order.get("visible") is False:
            continue

        user = order.get("user", {}) or {}
        status = user.get("status")

        try:
            price = float(order.get("platinum"))
        except (TypeError, ValueError):
            continue

        all_prices.append(price)

        if status == "ingame":
            ingame_prices.append(price)
        elif status == "online":
            online_prices.append(price)

    if ingame_prices:
        return min(ingame_prices)

    if online_prices:
        return min(online_prices)

    if all_prices:
        return min(all_prices)

    return None


def average_last_10_closed_sales(slug: str) -> float | None:
    try:
        response = requests.get(STATS_URL.format(slug), headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    payload = data.get("payload", {})
    closed = payload.get("statistics_closed", {})

    candidates = []

    if isinstance(closed, dict):
        for key in ("90days", "48hours"):
            value = closed.get(key)
            if isinstance(value, list):
                candidates.append(value)

        for value in closed.values():
            if isinstance(value, list):
                candidates.append(value)

    sales: list[float] = []

    for arr in candidates:
        for entry in reversed(arr):
            price = entry.get("avg_price")
            volume = entry.get("volume", 0)

            try:
                price = float(price)
                volume = int(volume)
            except (TypeError, ValueError):
                continue

            if volume <= 0:
                continue

            repeat = min(volume, 10 - len(sales))
            sales.extend([price] * repeat)

            if len(sales) >= 10:
                break

        if len(sales) >= 10:
            break

    if not sales:
        return None

    return round(sum(sales[:10]) / len(sales[:10]), 2)