import streamlit as st
import pandas as pd

from filtros import filtro_estados,filtro_status,filtro_tamanho_reclamacao,filtro_data
from graficos import serie_temporal,mapa_brasil_choropleth,grafico_pareto,proporcoes_resolucoes,estatistica_texto, nuvem_de_palavras, categorias_frequentes
from estatisticas import estatistica_estados,estatistica_casos

# streamlit run dashboard.py
st.title("DashBoard Carrefuor")

@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/RECLAMEAQUI_CARREFUOR.csv")

    return formatar_dados(df)

def formatar_dados(df):
    # formata as urls para o formato correto
    df["URL"] = df["URL"].str.replace("//","/")#formata o conteudo da coluna "TEMPO" para dia-mês-ano

    # converte de string para datetime
    df["TEMPO"] = pd.to_datetime(df["TEMPO"]).dt.strftime("%d-%m-%Y")
    df['TEMPO'] = pd.to_datetime(df['TEMPO'], dayfirst=True)

    # Na coluna "LOCAL" tinha informações faltando, tive que ir na url para corrigir
    df["LOCAL"] = df["LOCAL"].replace({
        "-- - SP": "São Bernardo dos Campos - SP",

        "naoconsta - naoconsta": "Campo Grande - MS",
        "naoconsta - --": "Curitiba - PR"

    })
    # Deixa tudo maisculo na coluna "LOCAL"
    df["LOCAL"] = df["LOCAL"].str.upper()

    # Divide a coluna "LOCAL" em duas (MUNICIPIO/CIDADE,ESTADO)
    df[["CIDADE/MUNICIPIO","ESTADO"]] = df["LOCAL"].str.split(" - ",expand=True)

    df["CATEGORIA"] = df["CATEGORIA"].str.split(r"<->| - ")
    
    df["CATEGORIA"] = df["CATEGORIA"].apply(
        lambda lista: [item.upper().strip() for item in lista] if isinstance(lista, list) else lista
    )

    # Apaga as demais colunas de tempo por que dá para pegar essas informações da coluna "TEMPO" e tambem apaga a coluna "LOCAL" já que dividimos ela
    df.drop(columns=["ANO","MES","DIA","DIA_DO_ANO","SEMANA_DO_ANO","DIA_DA_SEMANA","TRIMETRES","LOCAL"],inplace=True)

    return df

def kpi(df: pd.DataFrame):

    col1, col2, col3, col4 = st.columns(4)

    # Total de casos
    total_casos = len(df)

    # Casos últimos 30 dias
    if "TEMPO" in df.columns:
        ultimos_30 = df[df["TEMPO"] >= (df["TEMPO"].max() - pd.Timedelta(days=30))]
        total_30_dias = len(ultimos_30)
    else:
        total_30_dias = 0

    # Estado com mais casos
    estado_top = df["ESTADO"].value_counts().idxmax()

    categoria_top = (
        df["CATEGORIA"]
        .explode()
        .value_counts()
    )

    categoria_top = categoria_top[
        ~categoria_top.index.isin(["CARREFOUR", "LOJA FÍSICA","HIPERMERCADOS","SUPERMERCADOS"])
    ]

    categoria_principal = categoria_top.idxmax()

    # Exibição
    col1.metric("Estado líder", estado_top)
    col2.metric("Total de Casos", total_casos)
    col3.metric("Últimos 30 dias", total_30_dias)
    col4.metric("Categoria principal", categoria_principal)

carrefuor_df = carregar_dados()
carrefuor_df_filtrado = carrefuor_df.copy()
carrefuor_df_filtrado = filtro_data(carrefuor_df_filtrado)
carrefuor_df_filtrado = filtro_estados(carrefuor_df_filtrado)
carrefuor_df_filtrado = filtro_status(carrefuor_df_filtrado)
carrefuor_df_filtrado = filtro_tamanho_reclamacao(carrefuor_df_filtrado)

kpi(carrefuor_df_filtrado)
serie_temporal(carrefuor_df_filtrado)

mapa_brasil_choropleth(carrefuor_df_filtrado)
estatistica_estados(carrefuor_df_filtrado)

st.subheader("Distribuição Dos Reclamações E Status Dos Casos ")

grafico_pareto(carrefuor_df_filtrado)
proporcoes_resolucoes(carrefuor_df_filtrado)

estatistica_casos(carrefuor_df_filtrado)

st.subheader("Análise Do Conteudo Das Descrições e Categorias Frequentes")
estatistica_texto(carrefuor_df_filtrado)
categorias_frequentes(carrefuor_df_filtrado)

nuvem_de_palavras(carrefuor_df_filtrado)