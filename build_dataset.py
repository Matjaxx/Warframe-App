from __future__ import annotations

from pathlib import Path

from build_service import fetch_selected_relics_from_api_sync
from relic_loader import load_relic_data


def main() -> None:
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    all_relics = [f"{relic['name']} Relic" for relic in load_relic_data()]

    print(f"Total relics: {len(all_relics)}")

    df = fetch_selected_relics_from_api_sync(all_relics)

    if df.empty:
        print("Aucune donnée récupérée.")
        return

    xlsx_path = output_dir / "warframe_relic_rewards.xlsx"
    csv_path = output_dir / "warframe_relic_rewards.csv"

    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False)

    print("\nFichiers créés :")
    print(f"- {xlsx_path}")
    print(f"- {csv_path}")


if __name__ == "__main__":
    main()