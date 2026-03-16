from __future__ import annotations

import asyncio

from warframe_market.client import WarframeMarketClient

from ev_calculator import compute_ev_intact, compute_ev_radiant
from excel_export import export_excel
from models import RelicRow
from price_fetcher import average_last_10_closed_sales, best_sell_price
from relic_loader import extract_tier, load_relic_data
from reward_parser import reward_name, reward_slug, split_rewards


MAX_RELICS = 10  # remplace par None pour tout prendre


async def main() -> None:
    relics = load_relic_data(limit=MAX_RELICS)
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
            try:
                relic_name = f"{relic['name']} Relic"
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

                ev_intact = compute_ev_intact(
                    bronze_prices=[price_b1, price_b2, price_b3],
                    argent_prices=[price_a1, price_a2],
                    gold_price=price_g1,
                )

                ev_radiant = compute_ev_radiant(
                    bronze_prices=[price_b1, price_b2, price_b3],
                    argent_prices=[price_a1, price_a2],
                    gold_price=price_g1,
                )

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

                    ev_intact=ev_intact,
                    ev_radiant=ev_radiant,
                )

                rows.append(row)
                print(f"[{i}/{total}] OK - {relic_name}")

            except Exception as exc:
                print(f"[{i}/{total}] ERROR - {relic.get('name', 'unknown')} - {exc}")

    export_excel(rows, "warframe_relic_rewards.xlsx")
    print("\nExcel créé : warframe_relic_rewards.xlsx")


if __name__ == "__main__":
    asyncio.run(main())