import math


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


def get_refinement_probas(refinement: str) -> dict[str, float]:
    if refinement.lower() == "radiant":
        return RADIANT_PROBAS
    return INTACT_PROBAS


def _safe_price(value) -> float:
    if value is None:
        return 0.0

    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0

    if math.isnan(value):
        return 0.0

    return value


def expected_best_of_players(
    rewards: list[tuple[str, float | None, str]],
    refinement: str,
    players: int,
) -> float:
    probas = get_refinement_probas(refinement)

    values = []
    probs = []

    for _, price, bucket in rewards:
        values.append(_safe_price(price))
        probs.append(probas[bucket])

    expected = 0.0
    unique_values = sorted(set(values))

    def cdf(v: float) -> float:
        total = 0.0
        for value, prob in zip(values, probs):
            if value <= v:
                total += prob
        return total

    prev_cdf_players = 0.0

    for v in unique_values:
        current_cdf_players = cdf(v) ** players
        p_max_eq_v = current_cdf_players - prev_cdf_players
        expected += v * p_max_eq_v
        prev_cdf_players = current_cdf_players

    return round(expected, 2)


def effective_buy_price(total_buy_price: float, players: int) -> float:
    if players <= 0:
        return float(total_buy_price)
    return round(float(total_buy_price) / players, 2)


def compute_profit(expected_value: float, total_buy_price: float, players: int) -> float:
    shared_cost = effective_buy_price(total_buy_price, players)
    return round(float(expected_value) - shared_cost, 2)