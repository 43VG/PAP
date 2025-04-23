import streamlit as st           # Cria o site interativo
import pandas as pd             # Lê e trabalha com ficheiros Excel
import plotly.express as px     # Cria gráficos interativos
import plotly.io as pio         # Exporta gráficos como imagem ou PDF
import io                       # Cria ficheiros na memória

st.set_page_config(page_title="Visualizador de Excel", layout="wide")

# Título do site
st.markdown("""
    <h1 style='text-align: center; color: #3366cc;'>📊 Visualizador de Gráficos a partir de Excel</h1>
""", unsafe_allow_html=True)

# Upload múltiplo de ficheiros Excel
with st.expander("📁 Carrega os teus ficheiros Excel"):
    ficheiros_excel = st.file_uploader("Seleciona um ou mais ficheiros", type=["xlsx"], accept_multiple_files=True)

if ficheiros_excel:
    todos_dfs = []

    for ficheiro in ficheiros_excel:
        folhas = pd.ExcelFile(ficheiro).sheet_names
        folhas_escolhidas = st.multiselect(f"📄 Folhas de: {ficheiro.name}", folhas, default=folhas[:1])

        for folha in folhas_escolhidas:
            dados = pd.read_excel(ficheiro, sheet_name=folha)
            dados["Ficheiro"] = ficheiro.name
            dados["Folha"] = folha
            dados = dados.loc[:, ~dados.columns.str.contains("^Unnamed")]  # Elimina colunas tipo "Unnamed"
            todos_dfs.append(dados)

    if todos_dfs:
        df_final = pd.concat(todos_dfs, ignore_index=True)
        with st.expander("📋 Pré-visualização dos dados"): # Pré-visualização dos dados
            st.dataframe(df_final)
        st.markdown("## 🎨 Gráfico Personalizado")

        col1, col2 = st.columns(2)
        colunas_validas = [col for col in df_final.columns if col not in ["Ficheiro", "Folha"]]# Filtrar colunas válidas (exclui "Ficheiro" e "Folha")

        with col1:
            x_coluna = st.selectbox("🧩 Coluna X", colunas_validas)
        with col2:
            y_coluna = st.selectbox("🎯 Coluna Y", colunas_validas)

        tipo = st.selectbox("📈 Tipo de gráfico", ["Barras", "Linhas", "Pizza"])
        if tipo == "Barras":
            grafico = px.bar(df_final, x=x_coluna, y=y_coluna, title=f"{y_coluna} por {x_coluna}", color=x_coluna)
        elif tipo == "Linhas":
            dados_agrupados = df_final.groupby(x_coluna, as_index=False)[y_coluna].sum()
            grafico = px.line(dados_agrupados, x=x_coluna, y=y_coluna, title=f"{y_coluna} por {x_coluna}")
        elif tipo == "Pizza":
            grafico = px.pie(df_final, names=x_coluna, values=y_coluna, title=f"{y_coluna} por {x_coluna}")

        st.plotly_chart(grafico, use_container_width=True)

        # Botões de exportação
        col3, col4 = st.columns(2)

        with col3:
            if st.button("📥 Exportar Gráfico como PNG"):
                buffer_png = io.BytesIO()
                pio.write_image(grafico, buffer_png, format='png')
                st.download_button(
                    label="Descarregar PNG",
                    data=buffer_png.getvalue(),
                    file_name="grafico.png",
                    mime="image/png"
                )

        with col4:
            if st.button("📥 Exportar Gráfico como PDF"):
                buffer_pdf = io.BytesIO()
                pio.write_image(grafico, buffer_pdf, format='pdf')
                st.download_button(
                    label="Descarregar PDF",
                    data=buffer_pdf.getvalue(),
                    file_name="grafico.pdf",
                    mime="application/pdf"
                )

        # Secção de vários gráficos automáticos
        st.markdown("## 🧠 Gráficos Gerados Automaticamente")

        tipos_graficos = st.multiselect(
            "Seleciona os tipos de gráficos que queres gerar automaticamente:",
            ["Barras", "Linhas", "Pizza"]
        )

        colunas_numericas = df_final.select_dtypes(include='number').columns.tolist()
        colunas_texto = df_final.select_dtypes(include='object').columns.tolist()

        if not colunas_numericas or not colunas_texto:
            st.warning("É necessário ter pelo menos uma coluna de texto e uma coluna numérica.")
        else:
            coluna_x_auto = colunas_texto[0]
            if tipos_graficos:  # Só desenha se o utilizador escolher pelo menos um tipo, para nao aparecer erro
                colunas_layout = st.columns(len(tipos_graficos))
                for i, tipo in enumerate(tipos_graficos):
                    with colunas_layout[i]:
                        st.markdown(f"**Gráfico de {tipo}**")
                        if tipo == "Barras":
                            fig = px.bar(df_final, x=coluna_x_auto, y=colunas_numericas[0])
                        elif tipo == "Linhas":
                            df_agrupado = df_final.groupby(coluna_x_auto, as_index=False)[colunas_numericas[0]].sum()
                            fig = px.line(df_agrupado, x=coluna_x_auto, y=colunas_numericas[0])
                        elif tipo == "Pizza":
                            fig = px.pie(df_final, names=coluna_x_auto, values=colunas_numericas[0])
                        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Não foram encontrados dados nas folhas selecionadas.")
