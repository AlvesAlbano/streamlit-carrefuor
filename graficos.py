import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import spacy
import spacy.cli
import matplotlib.pyplot as plt

from collections import Counter
from wordcloud import WordCloud

def serie_temporal(df:pd.DataFrame):
    # Agrupar por data
    st.subheader("Evolução das Reclamações ao Longo do Ano")

    df = df.groupby("TEMPO").size().reset_index(name="QUANTIDADE_RECLAMACOES")

    # Ordenar
    df = df.sort_values("TEMPO")
    df = df.set_index("TEMPO").asfreq("D", fill_value=0).reset_index()

    # Média móvel (7 dias)
    media_movel_input = st.slider("Período da Média Móvel (dias)", 1, df.shape[0], 7)
    df["MEDIA_MOVEL"] = df["QUANTIDADE_RECLAMACOES"].rolling(window=media_movel_input).mean()

    # Gráfico
    st.line_chart(df.set_index("TEMPO").sort_index()[["QUANTIDADE_RECLAMACOES", "MEDIA_MOVEL"]])

def mapa_brasil_choropleth(df:pd.DataFrame):
    # 🔹 GeoJSON dos estados do Brasil
    st.header("Distribuição Geografica Das Reclamações")

    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson = requests.get(url).json()

    # 🔹 Agrupar dados por estado
    df_estado = df.groupby("ESTADO").size().reset_index(name="QUANTIDADE_RECLAMACOES")

    # 🔹 Criar mapa
    fig = px.choropleth(
        df_estado,
        geojson=geojson,
        locations="ESTADO",
        featureidkey="properties.sigla",  # chave do geojson
        color="QUANTIDADE_RECLAMACOES",
        color_continuous_scale="Reds"
    )

    # 🔥 Ajuste importante → MOSTRAR SÓ O BRASIL
    fig.update_geos(
        fitbounds="locations",  # encaixa no Brasil
        visible=False           # remove fundo/mundo
    )

    # 🔥 layout mais limpo
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_pareto(df:pd.DataFrame):

    # 🔹 agrupar e preparar dados
    df_estado = (
        df.groupby("ESTADO")
        .size()
        .reset_index(name="QUANTIDADE_RECLAMACOES")
        .sort_values(by="QUANTIDADE_RECLAMACOES", ascending=False)
    )

    # 🔹 percentual acumulado
    df_estado["perc_acum"] = (
        df_estado["QUANTIDADE_RECLAMACOES"].cumsum() /
        df_estado["QUANTIDADE_RECLAMACOES"].sum()
    )

    # 🔹 criar figura
    fig = go.Figure()

    # barras
    fig.add_bar(
        x=df_estado["ESTADO"],
        y=df_estado["QUANTIDADE_RECLAMACOES"],
        name="Reclamações"
    )

    # linha acumulada
    fig.add_scatter(
        x=df_estado["ESTADO"],
        y=df_estado["perc_acum"],
        name="% Acumulado",
        yaxis="y2",
        mode="lines+markers"
    )

    # linha 80%
    fig.add_hline(
        y=0.8,
        line_dash="dash",
        line_color="red"
    )

    # layout
    fig.update_layout(
        title="Pareto de Reclamações por Estado",
        xaxis_title="Estado",
        yaxis=dict(title="Quantidade"),
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            tickformat=".0%"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def proporcoes_resolucoes(df:pd.DataFrame):

    df_status = (
        df.groupby("STATUS")["CASOS"]
        .sum()
        .reset_index()
        .sort_values(by="CASOS",ascending=False)
    )

    fig = px.bar(
        df_status,
        x="STATUS",
        y="CASOS",
        text="CASOS",
        title="Casos por Status"
    )

    st.plotly_chart(fig, use_container_width=True)


def estatistica_texto(df:pd.DataFrame):

    df["TAMANHO_DESCRICAO"] = df["DESCRICAO"].str.len()

    df_status = (
        df.groupby("STATUS")["TAMANHO_DESCRICAO"]
        .mean()
        .reset_index()
        .sort_values(by="TAMANHO_DESCRICAO",ascending=False)
    )

    fig = px.bar(
        df_status,
        x="STATUS",
        y="TAMANHO_DESCRICAO",
        text="TAMANHO_DESCRICAO",
        title="Média Do Tamanho Da Descrição Por Status"
    )

    # fig = px.box(
    #     df,
    #     x="STATUS",
    #     y="TAMANHO_DESCRICAO",
    #     title="Distribuição do tamanho da descrição por status"
    # )

    fig.update_traces(
        texttemplate='%{text:.0f}'
    )

    st.plotly_chart(fig, use_container_width=True)

def nuvem_de_palavras(df):
    stopwords_adicionais = [
        "CARREFUOR", "NÃO", "HOJE", "COMIGO",
        "MELHOR", "CHEGAR", "DISSERAM", "ESPOSA"
        "VÁRIAS", "PASSOU", "FAZENDO", "CONFORME",
        "CARREFOUR", "ALGUMAS", "PESSOA", "PASSEI",
        "SIMPLESMENTE", "ALGUMA", "SENHORA" , "DEIXAR",
        "PODERIA", "CONSEGUI", "FALARAM", "VOLTEI", "SHOPPING",
        "PEGUEI", "FÍSICA", "RECEBI", "FAMÍLIA", "NENHUM", "QUEIJO",
        "AJUDAR", "VOLTAR", "PODERIA", "GOSTARIA", "RESOLVER", "NOVAMENTE",
        "REALIZEI", "FRENTE" , "PASSAR", "ENTRADA", "DIZENDO", "SEMANA", "SURPRESA",
        "ESPOSA", "FIQUEI", "ESTAVAM", "HIPERMERCADO", "PRECISO", "PERGUNTAR", "MESMOS",
        "SUPERMERCADO", "TOTALMENTE", "APRESENTOU", "EFETUAR", "NINGUÉM", "EXTREMAMENTE" , "QUESTIONEI",
        "VÁRIAS", "REALMENTE","DOCUMENTOS", "MINUTOS", "OCORRÊNCIA", "PROCURAR", "EDITADO" , "CELULAR", "NOTEBOOK",
        "ACONTECE", "DIFERENTE", "MÍNIMO", "TELEFONE", "COMPRO", "COISAS", "TÉCNICA", "PEDIDO", "CIDADE", "ENTRAR", "TIVESSE",
        "RETIRAR", "PACOTE", "OCORREU", "EXPRESS", "TÉCNICA", "SEGURO", "ENTREI", "MARIDO", "PŔOPRIA", "VERDADE", "ENTREGA", "PRECISAVA",
        "ERRADO", "RESPONDEU", "DEVIDO", "AGUARDO", "VONTADE", "PERCEBI", "BRASIL", "ACABEI", "PASSARAM", "AVENIDA", "SOLUÇÃO", "ALGUEM", "SÁBADO",
        "FALANDO", "NECESSARIO", "ENTENDER", "INFELIZMENTE", "LIGAÇÃO", "ATENDEU", "CHAMAR", "TAMANHO", "PASSANDO", "ALEGANDO", "TINHAM", "RETORNO", "LOCALIZADO",
        "ENTENDO", "AFINAL"
    ]

    try:
        nlp = spacy.load("pt_core_news_sm")
    except OSError:
        spacy.cli.download("pt_core_news_sm")
        nlp = spacy.load("pt_core_news_sm")

    palavras_importantes = []
    for texto in df['DESCRICAO']:
        doc = nlp(str(texto).upper())

        for token in doc:
            if (
                token.is_alpha and
                not token.is_stop and
                token.pos_ not in ["VERB", "AUX"] and
                token.lemma_ not in stopwords_adicionais and
                len(token.lemma_) > 5 and
                token.lemma_ not in stopwords_adicionais
            ):
                palavras_importantes.append(token.lemma_)

    frequencia = Counter(palavras_importantes)
    # print(frequencia)

    # 🔥 cria a wordcloud
    wordcloud = WordCloud(
        width=1400,
        height=1400,
        background_color="white"
    ).generate_from_frequencies(frequencia)

    # 🔥 plot
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")

    # 🔥 streamlit
    st.subheader("Nuvem De Palavras Mais Frequentes")
    st.pyplot(fig)

def categorias_frequentes(df: pd.DataFrame):

    df_explodido = df.explode("CATEGORIA")

    contagem = (
        df_explodido
        .groupby(["CATEGORIA", "STATUS"])
        .size()
        .reset_index(name="FREQUENCIA")
    )

    contagem = contagem[
        ~contagem["CATEGORIA"].isin(["CARREFOUR", "LOJA FÍSICA","HIPERMERCADOS","SUPERMERCADOS"])
    ]

    top_categorias = (
        contagem
        .groupby("CATEGORIA")["FREQUENCIA"]
        .sum()
        .nlargest(10)
        .index
    )

    contagem = contagem[contagem["CATEGORIA"].isin(top_categorias)]

    contagem = contagem.sort_values(by="FREQUENCIA", ascending=True)

    fig = px.bar(
        contagem,
        x="FREQUENCIA",
        y="CATEGORIA",
        color="STATUS",
        text="FREQUENCIA",
        orientation="h",
        title="Top 10 Categorias Mais Frequentes",
        barmode="group"
    )

    fig.update_traces(textposition="outside")

    taxa = (df["STATUS"] == "Resolvido").mean() * 100
    st.metric("Taxa de Resolução", f"{taxa:.1f}%")
    
    st.plotly_chart(fig, use_container_width=True)