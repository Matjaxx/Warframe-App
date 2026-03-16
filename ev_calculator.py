INTACT_PROBAS = {
    "bronze": 0.2533,
    "argent": 0.11,
    "gold": 0.02,
}

RADIANT_PROBAS = {
    "bronze": 0.1667,
    "argent": 0.20,
    "gold": 0.10,
}


def _safe_price(value: float | None) -> float:
    return 0.0 if value is None else float(value)


def compute_ev_intact(
    bronze_prices: list[float | None],
    argent_prices: list[float | None],
    gold_price: float | None,
) -> float:
    value = 0.0

    for price in bronze_prices:
        value += INTACT_PROBAS["bronze"] * _safe_price(price)

    for price in argent_prices:
        value += INTACT_PROBAS["argent"] * _safe_price(price)

    value += INTACT_PROBAS["gold"] * _safe_price(gold_price)

    return round(value, 2)


def compute_ev_radiant(
    bronze_prices: list[float | None],
    argent_prices: list[float | None],
    gold_price: float | None,
) -> float:
    value = 0.0

    for price in bronze_prices:
        value += RADIANT_PROBAS["bronze"] * _safe_price(price)

    for price in argent_prices:
        value += RADIANT_PROBAS["argent"] * _safe_price(price)

    value += RADIANT_PROBAS["gold"] * _safe_price(gold_price)

    return round(value, 2)