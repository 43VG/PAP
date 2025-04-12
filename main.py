import streamlit as st           # Cria o site interativo
import pandas as pd             # Lê e trabalha com ficheiros Excel
import plotly.express as px     # Cria gráficos interativos
import plotly.io as pio         # Exporta gráficos como imagem ou PDF
import io                       # Cria ficheiros na memória
from pathlib import Path        # Lida com caminhos (não está a ser usado aqui)

# Define o título da aba e o layout do site
st.set_page_config(page_title="Visualizador de Excel", layout="wide")  

# Título do site
st.title("📊 Visualizador de Gráficos a partir de Excel")  

# Input para carregar vários ficheiros Excel
uploaded_files = st.file_uploader("Carrega os teus ficheiros Excel", type=["xlsx"], accept_multiple_files=True)  # Upload múltiplo

# Se o utilizador carregar ficheiros
if uploaded_files:
    todos_dfs = []  # Lista para guardar os DataFrames

    for uploaded_file in uploaded_files:
        folhas = pd.ExcelFile(uploaded_file).sheet_names  # Lista folhas do Excel
        folha_selecionada = st.selectbox(f"Escolhe a folha de: {uploaded_file.name}", folhas)  # Seleciona folha por ficheiro
        df = pd.read_excel(uploaded_file, sheet_name=folha_selecionada)  # Lê a folha
        df["Fonte"] = uploaded_file.name  # Adiciona nome do ficheiro
        todos_dfs.append(df)  # Junta à lista

    df = pd.concat(todos_dfs, ignore_index=True)  # Junta todos os dados

    # Mostra a tabela
    st.subheader("Pré-visualização dos dados:")
    st.dataframe(df)

    if not df.empty:
        st.subheader("Gráfico Personalizado")

        colunas = df.columns.tolist()  # Lista de colunas

        # Seleciona colunas X e Y
        x_col = st.selectbox("Seleciona a coluna X", colunas)
        y_col = st.selectbox("Seleciona a coluna Y", colunas)

        # Permite escolher o tipo de gráfico
        tipo_grafico = st.selectbox("Escolhe o tipo de gráfico", ["Barras", "Linhas", "Pizza"])

        # Gera o gráfico com base na escolha
        if tipo_grafico == "Barras":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}", color=x_col)  # Gráfico de barras
        elif tipo_grafico == "Linhas":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}")  # Gráfico de linhas
        elif tipo_grafico == "Pizza":
            fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} por {x_col}")  # Gráfico de pizza

        # Mostra o gráfico no site
        st.plotly_chart(fig, use_container_width=True)

        # Botão para exportar como PNG
        if st.button("📥 Exportar Gráfico como Imagem PNG"):
            buffer_img = io.BytesIO()                     # Cria buffer para imagem
            pio.write_image(fig, buffer_img, format='png')  # Grava imagem no buffer
            st.download_button(                           # Botão para descarregar PNG
                label="Descarregar PNG",
                data=buffer_img.getvalue(),
                file_name="grafico.png",
                mime="image/png"
            )

        # Botão para exportar como PDF
        if st.button("📥 Exportar Gráfico como PDF"):
            buffer_pdf = io.BytesIO()                     # Cria buffer para PDF
            pio.write_image(fig, buffer_pdf, format='pdf')  # Grava PDF no buffer
            st.download_button(                           # Botão para descarregar PDF
                label="Descarregar PDF",
                data=buffer_pdf.getvalue(),
                file_name="grafico.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("A folha selecionada está vazia.")
