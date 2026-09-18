import streamlit as st
import pandas as pd
from clickhouse_driver import Client

st.set_page_config(page_title="Gravitational Waves", layout="wide")
st.title("🌌 Каталог гравитационно-волновых событий")


@st.cache_data(ttl=60)
def load_data():
    client = Client(
        host="localhost",
        port=9000,
        user="default",
        password="clickhouse",
        database="gw_v2",
    )
    rows = client.execute(
        """
        SELECT common_name, total_mass_source, luminosity_distance,
               network_snr, merger_type
        FROM gw_v2.events
        """
    )
    return pd.DataFrame(
        rows,
        columns=["common_name", "total_mass", "distance", "snr", "merger_type"],
    )


df = load_data()

if df.empty:
    st.warning("Данных пока нет. Сначала запусти load.py из прошлого урока.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Всего событий", len(df))
col2.metric("Слияний чёрных дыр (BBH)", int((df["merger_type"] == "BBH").sum()))
col3.metric("Слияний нейтронных звёзд (BNS)", int((df["merger_type"] == "BNS").sum()))

st.subheader("Типы слияний")
st.bar_chart(df["merger_type"].value_counts())
st.caption(
    "Почти все события — слияния чёрных дыр (BBH). Их видно с большого "
    "расстояния, поэтому ловят их чаще, чем лёгкие нейтронные звёзды (BNS)."
)

st.subheader("Масса и расстояние событий")
st.scatter_chart(
    df,
    x="total_mass",
    y="distance",
    color="merger_type",
)
st.caption(
    "Каждая точка — реальное слияние. Чем тяжелее событие (правее), тем "
    "дальше его видно (выше). Одинокая точка слева внизу — GW170817: "
    "лёгкое слияние нейтронных звёзд, которое поймали только потому, что "
    "оно произошло совсем близко."
)

st.subheader("Все события")
st.dataframe(
    df.sort_values("total_mass", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "common_name": st.column_config.TextColumn("Событие"),
        "total_mass": st.column_config.NumberColumn("Суммарная масса (☉)", format="%.1f"),
        "distance": st.column_config.NumberColumn("Расстояние (Mpc)", format="%.0f"),
        "snr": st.column_config.NumberColumn("Сила сигнала (SNR)", format="%.1f"),
        "merger_type": st.column_config.TextColumn("Тип слияния"),
    },
)