from __future__ import annotations

import asyncio
from dataclasses import asdict

import pandas as pd
from warframe_market.client import WarframeMarketClient

from ev_calculator import compute_ev_intact, compute_ev_radiant
from models import RelicRow
from price_fetcher import average_last_10_closed_sales, best_sell_price
from relic_loader import extract_tier, load_relic_data
from reward_parser import reward_name, reward_slug, split_rewards


async def fetch_selected_relics_from_api(selected_relic_names: list[str]) -> pd.DataFrame:
    all_relics = load_relic_data()
    wanted = set(selected_relic_names)

    relics = [
        relic
        for relic in all_relics
        if f"{relic['name']} Relic" in wanted
    ]

    rows: list[RelicRow] = []

    async with WarframeMarketClient() as client:
        price_cache: dict[str, float | None] = {}

        async def get_price(slug: str | None) -> float | None:
            if slug is None:
                return None

            if slug in price_cache:
                return price_cache[slug]

            price: float | None = None

            try:
                orders = await client.get_top_orders_for_item(slug)
                price = best_sell_price(orders)
            except Exception:
                price = None

            if price is None:
                price = average_last_10_closed_sales(slug)

            price_cache[slug] = price
            return price

        total = len(relics)

        for i, relic in enumerate(relics, start=1):
            relic_name = f"{relic['name']} Relic"
            print(f"[{i}/{total}] Fetching {relic_name}")

            try:
                rewards = relic.get("rewards", [])

                bronze, argent, gold = split_rewards(rewards)

                b1, b2, b3 = bronze
                a1, a2 = argent
                g1 = gold[0]

                price_b1 = await get_price(reward_slug(b1))
                price_b2 = await get_price(reward_slug(b2))
                price_b3 = await get_price(reward_slug(b3))
                price_a1 = await get_price(reward_slug(a1))
                price_a2 = await get_price(reward_slug(a2))
                price_g1 = await get_price(reward_slug(g1))

                row = RelicRow(
                    relic_name=relic_name,
                    tier=extract_tier(relic_name),
                    item_bronze1=reward_name(b1),
                    price_bronze1=price_b1,
                    item_bronze2=reward_name(b2),
                    price_bronze2=price_b2,
                    item_bronze3=reward_name(b3),
                    price_bronze3=price_b3,
                    item_argent1=reward_name(a1),
                    price_argent1=price_a1,
                    item_argent2=reward_name(a2),
                    price_argent2=price_a2,
                    item_gold1=reward_name(g1),
                    price_gold1=price_g1,
                    ev_intact=compute_ev_intact(
                        bronze_prices=[price_b1, price_b2, price_b3],
                        argent_prices=[price_a1, price_a2],
                        gold_price=price_g1,
                    ),
                    ev_radiant=compute_ev_radiant(
                        bronze_prices=[price_b1, price_b2, price_b3],
                        argent_prices=[price_a1, price_a2],
                        gold_price=price_g1,
                    ),
                )

                rows.append(row)

            except Exception as exc:
                print(f"ERROR on {relic_name}: {exc}")

    return pd.DataFrame(asdict(row) for row in rows)


def fetch_selected_relics_from_api_sync(selected_relic_names: list[str]) -> pd.DataFrame:
    return asyncio.run(fetch_selected_relics_from_api(selected_relic_names))