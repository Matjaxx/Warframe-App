import pandas as pd
import streamlit as st

from app_service import fetch_one_relic_details_sync, fetch_selected_relics_sync
from vision_calculator import (
    compute_profit,
    effective_buy_price,
    expected_best_of_players,
)

st.set_page_config(page_title="Warframe Relic App", layout="wide")

# =========================
# LOAD DATASET
# =========================
all_df = fetch_selected_relics_sync([])
all_relics = sorted(all_df["relic_name"].dropna().unique().tolist())

# =========================
# NAV STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "Relic Browser"


def go_to(page_name: str) -> None:
    st.session_state.page = page_name


# =========================
# SIDEBAR NAVBAR
# =========================
st.sidebar.title("Warframe Relic App")
st.sidebar.caption("Navigation")

if st.sidebar.button(
    "📊 Relic Browser",
    use_container_width=True,
    type="primary" if st.session_state.page == "Relic Browser" else "secondary",
):
    go_to("Relic Browser")

if st.sidebar.button(
    "🔮 Relic Vision",
    use_container_width=True,
    type="primary" if st.session_state.page == "Relic Vision" else "secondary",
):
    go_to("Relic Vision")

st.sidebar.divider()
st.sidebar.write(f"Page active : **{st.session_state.page}**")

page = st.session_state.page

# =========================
# RELIC BROWSER
# =========================
if page == "Relic Browser":
    st.title("📊 Relic Browser")
    st.caption("Analyse multi-relics avec EV et prix")

    selected_relics = st.multiselect(
        "Sélectionne une ou plusieurs relics (vide = toutes)",
        options=all_relics,
        default=[],
    )

    col1, col2 = st.columns(2)

    with col1:
        sort_by = st.selectbox(
            "Trier par",
            options=["relic_name", "ev_intact", "ev_radiant"],
            index=1,
        )

    with col2:
        ascending = st.checkbox("Tri croissant", value=False)

    relics_to_fetch = selected_relics if selected_relics else all_relics
    df = fetch_selected_relics_sync(relics_to_fetch)

    if not df.empty:
        df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger CSV",
            csv,
            "relics_filtered.csv",
            use_container_width=True,
        )
    else:
        st.info("Aucune donnée.")

# =========================
# RELIC VISION
# =========================
elif page == "Relic Vision":
    st.title("🔮 Relic Vision")
    st.caption("Calcul de profit avec squad")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_relic = st.selectbox("Relic", options=all_relics)

    with col2:
        refinement = st.selectbox("Refinement", ["Intact", "Radiant"])

    with col3:
        players = st.selectbox("Players", [3, 4], index=1)

    with col4:
        buy_price = st.number_input("Prix total", min_value=0.0, value=0.0)

    details = fetch_one_relic_details_sync(selected_relic)

    if not details:
        st.error("Erreur chargement relic.")
    else:
        rewards = details["rewards"]

        expected_value = expected_best_of_players(
            rewards=rewards,
            refinement=refinement,
            players=players,
        )

        shared_cost = effective_buy_price(buy_price, players)
        profit = compute_profit(expected_value, buy_price, players)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Relic", details["relic_name"])
        m2.metric("EV équipe", expected_value)
        m3.metric("Coût / joueur", shared_cost)
        m4.metric("Profit", profit)

        st.subheader("Rewards")

        df_rewards = pd.DataFrame(
            [
                {
                    "item": name,
                    "price": price,
                    "rarity": rarity,
                }
                for name, price, rarity in rewards
            ]
        )

        st.dataframe(df_rewards, use_container_width=True, hide_index=True)

        st.subheader("EV solo")
        c1, c2 = st.columns(2)
        c1.metric("EV Intact", details["ev_intact"])
        c2.metric("EV Radiant", details["ev_radiant"])