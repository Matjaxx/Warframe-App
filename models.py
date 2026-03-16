from dataclasses import dataclass


@dataclass
class RelicRow:
    relic_name: str
    tier: str | None

    item_bronze1: str | None
    price_bronze1: float | None

    item_bronze2: str | None
    price_bronze2: float | None

    item_bronze3: str | None
    price_bronze3: float | None

    item_argent1: str | None
    price_argent1: float | None

    item_argent2: str | None
    price_argent2: float | None

    item_gold1: str | None
    price_gold1: float | None

    ev_intact: float | None
    ev_radiant: float | None