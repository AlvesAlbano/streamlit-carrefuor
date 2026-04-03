import streamlit as st
import pandas as pd

from collections import Counter
from wordcloud import WordCloud

def estatistica_estados(df: pd.DataFrame):

    st.subheader("Principais Reclamações de Cada Estado")

    estados = df["ESTADO"].dropna().unique()

    for estado in estados:
        df_estado = df[df["ESTADO"] == estado]

        if df_estado.empty:
            continue

        # Cidade mais crítica
        cidade_series = df_estado["CIDADE/MUNICIPIO"].dropna()

        if not cidade_series.empty:
            cidade_top = cidade_series.value_counts().idxmax()
        else:
            cidade_top = "Sem dados"

        # Categorias
        categoria_series = (
            df_estado["CATEGORIA"]
            .explode()
            .dropna()
            .astype(str)
            .str.strip()
        )

        # remove categorias indesejadas
        categoria_series = categoria_series[
            ~categoria_series.isin([
                "CARREFOUR", "LOJA FÍSICA","HIPERMERCADOS","SUPERMERCADOS"
            ])
        ]

        # 🔥 valida antes de usar idxmax
        if not categoria_series.empty:
            categoria_top = categoria_series.value_counts().idxmax()
        else:
            categoria_top = "Sem dados"

        # UI
        st.subheader(f"Estado - {estado}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Cidade/Município mais crítico", cidade_top)

        with col2:
            st.metric("Categoria mais frequente", categoria_top)


def estatistica_casos(df: pd.DataFrame):
    st.subheader("Principais Status de Cada Estado")

    estados = df["ESTADO"].dropna().unique()

    for estado in estados:
        df_estado = df[df["ESTADO"] == estado]

        if df_estado.empty:
            continue

        # Cidade mais crítica
        cidade_series = df_estado["CIDADE/MUNICIPIO"].dropna()

        if not cidade_series.empty:
            cidade_top = cidade_series.value_counts().idxmax()
        else:
            cidade_top = "Sem dados"

        # Status mais frequente
        status_series = df_estado["STATUS"].dropna().astype(str).str.strip()

        if not status_series.empty:
            status_top = status_series.value_counts().idxmax()
        else:
            status_top = "Sem dados"

        # UI
        st.subheader(f"Estado - {estado}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Cidade/Município mais crítico", cidade_top)

        with col2:
            st.metric("Status mais frequente", status_top)