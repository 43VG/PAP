import streamlit as st          # Cria o site interativo
import pandas as pd             # Lê e trabalha com ficheiros Excel
import plotly.express as px     # Cria gráficos interativos
import plotly.io as pio         # Exporta imagens
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
            dados = pd.read_excel(ficheiro, sheet_name=folha, header=None)
            primeira_linha_valida = dados.dropna(how='all').index.min()
            dados = pd.read_excel(ficheiro, sheet_name=folha, skiprows=primeira_linha_valida)
            dados["Ficheiro"] = ficheiro.name
            dados["Folha"] = folha
            dados = dados.loc[:, ~dados.columns.str.contains("^Unnamed")]
            todos_dfs.append(dados)

    if todos_dfs:
        df_final = pd.concat(todos_dfs, ignore_index=True)
        with st.expander("📋 Pré-visualização dos dados"):
            st.dataframe(df_final)

        # Gráficos automáticos
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
            coluna_x_auto = st.selectbox("🧩 Coluna de Texto (X ou Nomes)", colunas_texto)
            coluna_y_auto = st.selectbox("🎯 Coluna Numérica (Y ou Valores)", colunas_numericas)

            if tipos_graficos:
                colunas_layout = st.columns(len(tipos_graficos))
                for i, tipo in enumerate(tipos_graficos):
                    with colunas_layout[i]:
                        st.markdown(f"**Gráfico de {tipo}**")
                        if tipo == "Barras":
                            fig = px.bar(df_final, x=coluna_x_auto, y=coluna_y_auto)
                        elif tipo == "Linhas":
                            df_agrupado = df_final.groupby(coluna_x_auto, as_index=False)[coluna_y_auto].sum()
                            fig = px.line(df_agrupado, x=coluna_x_auto, y=coluna_y_auto)
                        elif tipo == "Pizza":
                            fig = px.pie(df_final, names=coluna_x_auto, values=coluna_y_auto)
                        st.plotly_chart(fig, use_container_width=True)

                        # Exportação
                        col3, col4 = st.columns(2)
                        with col3:
                            if st.button(f"📥 Exportar {tipo} como PNG", key=f"{tipo}_png"):
                                buffer_png = io.BytesIO()
                                pio.write_image(fig, buffer_png, format='png')
                                st.download_button(
                                    label="Descarregar PNG",
                                    data=buffer_png.getvalue(),
                                    file_name=f"grafico_{tipo.lower()}.png",
                                    mime="image/png"
                                )
                        with col4:
                            if st.button(f"📥 Exportar {tipo} como PDF", key=f"{tipo}_pdf"):
                                buffer_pdf = io.BytesIO()
                                pio.write_image(fig, buffer_pdf, format='pdf')
                                st.download_button(
                                    label="Descarregar PDF",
                                    data=buffer_pdf.getvalue(),
                                    file_name=f"grafico_{tipo.lower()}.pdf",
                                    mime="application/pdf"
                                )
    else:
        st.warning("Não foram encontrados dados nas folhas selecionadas.")
