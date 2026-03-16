import requests

WM_STATS_URL = "https://api.warframe.market/v1/items/{}/statistics"


def get_order_status(order) -> str | None:
    user = getattr(order, "user", None)
    if user is None:
        return None
    return getattr(user, "status", None)


def best_sell_price(top_orders) -> float | None:
    sell_orders = getattr(top_orders.data, "sell", []) or []
    if not sell_orders:
        return None

    ingame_prices: list[float] = []
    online_prices: list[float] = []
    all_prices: list[float] = []

    for order in sell_orders:
        try:
            price = float(order.platinum)
        except (TypeError, ValueError):
            continue

        status = get_order_status(order)
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
    headers = {
        "Platform": "pc",
        "Language": "en",
        "Accept": "application/json",
        "User-Agent": "warframe-relic-streamlit/1.0",
    }

    try:
        response = requests.get(WM_STATS_URL.format(slug), headers=headers, timeout=30)
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