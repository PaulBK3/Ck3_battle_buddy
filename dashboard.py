import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt

# -----------------------
# Load Data
# -----------------------
def dashboard(data):
    st.title("CK3 Battle Tracker Dashboard")

    battles = json.load(data)

    # Flatten the JSON into a DataFrame
    rows = []
    for battle in battles["battles"]:
        for side in battle["sides"]:
            for reg in side["regiments"]:
                rows.append({
                    "battle_id": battle["battle_id"],
                    "location": battle["location"],
                    "side": side["side"],
                    "commander": side["commander_id"],
                    "type": reg["type"],
                    "knight": reg["knight"],
                    "initial_count": reg["initial_count"],
                    "final_count": reg["final_count"],
                    "main_kills": reg["main_kills"],
                    "pursuit_kills": reg["pursuit_kills"],
                    "main_losses": reg["main_losses"],
                    "pursuit_losses_self": reg["pursuit_losses_self"],
                    "pursuit_losses_maa": reg["pursuit_losses_maa"],
                    "damage_last_tick": reg["damage_last_tick"]
                })
    df = pd.DataFrame(rows)

    st.subheader("Battle Data Overview")
    st.dataframe(df)

    # Add calculated fields
    df["total_kills"] = df["main_kills"] + df["pursuit_kills"]
    df["total_losses"] = df["main_losses"] + df["pursuit_losses_self"] + df["pursuit_losses_maa"]

    # -----------------------
    # Filters
    # -----------------------
    st.sidebar.header("Filters")
    battle_ids = st.sidebar.multiselect("Select Battle(s)", df["battle_id"].unique())
    commanders = st.sidebar.multiselect("Select Commander(s)", df["commander"].unique())
    regiment_types = st.sidebar.multiselect("Select Regiment Type(s)", df["type"].unique())

    filtered_df = df.copy()
    if battle_ids:
        filtered_df = filtered_df[filtered_df["battle_id"].isin(battle_ids)]
    if commanders:
        filtered_df = filtered_df[filtered_df["commander"].isin(commanders)]
    if regiment_types:
        filtered_df = filtered_df[filtered_df["type"].isin(regiment_types)]

    # -----------------------
    # Charts
    # -----------------------
    st.subheader("Charts")

    # Top commanders by kills
    st.write("### Top Commanders by Total Kills")
    commander_kills = filtered_df.groupby("commander")["total_kills"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(commander_kills)

    # Regiment effectiveness
    st.write("### Regiment Types by Total Kills")
    regiment_kills = filtered_df.groupby("type")["total_kills"].sum().sort_values(ascending=False)
    st.bar_chart(regiment_kills)

    # Kills vs Losses per side
    st.write("### Side Performance (Kills vs Losses)")
    side_stats = filtered_df.groupby("side")[["total_kills", "total_losses"]].sum()
    st.bar_chart(side_stats)

    # Detailed table
    st.write("### Detailed Data")
    st.dataframe(filtered_df)
