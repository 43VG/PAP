import streamlit as st           # Cria o site interativo
import pandas as pd             # Lê e trabalha com ficheiros Excel
import plotly.express as px     # Cria gráficos interativos
import plotly.io as pio         # Exporta gráficos como imagem ou PDF
import io                       # Cria ficheiros na memória
from pathlib import Path        # Lida com caminhos (não está a ser usado aqui)

# Define o título da aba e o layout do site
st.set_page_config(page_title="Visualizador de Excel", layout="wide")

# Cabeçalho principal (com HTML)
st.markdown("""
    <h1 style='text-align: center; color: #3366cc;'>📊 Visualizador de Gráficos a partir de Excel</h1>
""", unsafe_allow_html=True)

# Input para carregar vários ficheiros Excel
with st.expander("📁 Carrega os teus ficheiros Excel"):
    uploaded_files = st.file_uploader("Seleciona um ou mais ficheiros", type=["xlsx"], accept_multiple_files=True)  # Upload múltiplo

# Se o utilizador carregar ficheiros
if uploaded_files:
    todos_dfs = []  # Lista para guardar os DataFrames

    for uploaded_file in uploaded_files:
        folhas = pd.ExcelFile(uploaded_file).sheet_names  # Lista folhas do Excel
        folhas_selecionadas = st.multiselect(f"📄 Folhas de: {uploaded_file.name}", folhas, default=folhas[:1])  # Seleção múltipla

        for folha in folhas_selecionadas:
            df = pd.read_excel(uploaded_file, sheet_name=folha)  # Lê folha
            df["Fonte"] = uploaded_file.name  # Adiciona nome do ficheiro
            df["Folha"] = folha  # Adiciona nome da folha
            todos_dfs.append(df)  # Adiciona ao conjunto final

    df = pd.concat(todos_dfs, ignore_index=True)  # Junta todos os dados num só DataFrame

    # Secção da tabela
    with st.expander("📋 Pré-visualização dos dados"):
        st.dataframe(df)  # Mostra a tabela

    if not df.empty:
        st.markdown("## 🎨 Gráfico Personalizado")  # Subtítulo da secção de gráficos

        col1, col2 = st.columns(2)  # Divide filtros em duas colunas

        colunas = df.columns.tolist()  # Lista de colunas do DataFrame

        with col1:
            x_col = st.selectbox("🧩 Coluna X", colunas)  # Seleciona eixo X
        with col2:
            y_col = st.selectbox("🎯 Coluna Y", colunas)  # Seleciona eixo Y

        tipo_grafico = st.selectbox("📈 Tipo de gráfico", ["Barras", "Linhas", "Pizza"])  # Escolha do tipo de gráfico

        # Gera gráfico consoante o tipo escolhido
        if tipo_grafico == "Barras":
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}", color=x_col)  # Gráfico de barras
        elif tipo_grafico == "Linhas":
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}")  # Gráfico de linhas
        elif tipo_grafico == "Pizza":
            fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} por {x_col}")  # Gráfico de pizza

        st.plotly_chart(fig, use_container_width=True)  # Mostra gráfico no ecrã

        col3, col4 = st.columns(2)  # Botões lado a lado

        with col3:
            if st.button("📥 Exportar Gráfico como PNG"):  # Botão para exportar como imagem
                buffer_img = io.BytesIO()  # Cria buffer na memória
                pio.write_image(fig, buffer_img, format='png')  # Grava imagem no buffer
                st.download_button(  # Botão para descarregar imagem
                    label="Descarregar PNG",
                    data=buffer_img.getvalue(),
                    file_name="grafico.png",
                    mime="image/png"
                )

        with col4:
            if st.button("📥 Exportar Gráfico como PDF"):  # Botão para exportar como PDF
                buffer_pdf = io.BytesIO()  # Cria buffer na memória
                pio.write_image(fig, buffer_pdf, format='pdf')  # Grava PDF no buffer
                st.download_button(  # Botão para descarregar PDF
                    label="Descarregar PDF",
                    data=buffer_pdf.getvalue(),
                    file_name="grafico.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("A folha selecionada está vazia.")  # Alerta se não houver dados
