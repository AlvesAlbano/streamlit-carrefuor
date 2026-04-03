import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


def filtro_estados(df: pd.DataFrame):

    estados = sorted(df["ESTADO"].dropna().unique())

    # default dinâmico (interseção)
    default_estados = [e for e in ["SP","RJ","MG","RS","PR"] if e in estados]

    estados_selecionados = st.sidebar.multiselect(
        "Filtrar Por Estado",
        options=estados,
        default=default_estados
    )

    df_filtrado = df[df["ESTADO"].isin(estados_selecionados)]

    return df_filtrado

def filtro_status(df:pd.DataFrame):
    # 🔹 filtro de estados
    status = sorted(df["STATUS"].unique())

    status_selecionados = st.sidebar.multiselect(
        "Filtrar Por Status",
        options=status,
        default=status
    )

    df_filtrado = df[
        df["STATUS"].isin(status_selecionados)
    ]

    return df_filtrado

def filtro_tamanho_reclamacao(df:pd.DataFrame):
    df["TAMANHO_DESCRICAO"] = df["DESCRICAO"].str.len()

    valor_max = int(df["TAMANHO_DESCRICAO"].max())
    valor_min = int(df["TAMANHO_DESCRICAO"].min())

    intervalo = st.sidebar.slider(
        "Tamanho Da Reclamação (Quantidade De Caracteres)",
        min_value=valor_min,
        max_value=valor_max,
        value=(valor_min,valor_max)
    )

    df_filtrado = df[
        (df["TAMANHO_DESCRICAO"] >= intervalo[0]) &
        (df["TAMANHO_DESCRICAO"] <= intervalo[1])
    ]

    return df_filtrado

def filtro_data(df: pd.DataFrame):

    df["TEMPO"] = pd.to_datetime(df["TEMPO"])

    data_min = df["TEMPO"].min()
    data_max = df["TEMPO"].max()

    intervalo_datas = st.sidebar.date_input(
        "Selecione O Período",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )

    if len(intervalo_datas) == 2:
        data_inicio, data_fim = intervalo_datas

        df_filtrado = df[
            (df["TEMPO"] >= pd.to_datetime(data_inicio)) &
            (df["TEMPO"] <= pd.to_datetime(data_fim))
        ]
    else:
        df_filtrado = df

    return df_filtrado