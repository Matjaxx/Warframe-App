import pandas as pd
from dataclasses import asdict


def autosize(ws):

    for col in ws.columns:

        length = 0
        letter = col[0].column_letter

        for cell in col:

            if cell.value:
                length = max(length, len(str(cell.value)))

        ws.column_dimensions[letter].width = min(length + 2, 40)


def export_excel(rows, path="relic_prices.xlsx"):

    df = pd.DataFrame(asdict(r) for r in rows)

    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="relics", index=False)

        ws = writer.sheets["relics"]

        ws.freeze_panes = "A2"

        autosize(ws)