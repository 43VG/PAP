import pandas as pd

def obter_folhas_excel(ficheiro):
    """Devolve os nomes das folhas do Excel"""
    try:
        excel_file = pd.ExcelFile(ficheiro)
        return excel_file.sheet_names
    except Exception as e:
        print(f"Erro ao obter folhas: {e}")
        return []

def ler_folhas_selecionadas(ficheiro, folhas_escolhidas):
    """Lê apenas as folhas escolhidas e devolve o DataFrame final"""
    todos_dfs = []
    for folha in folhas_escolhidas:
        try:
            dados = pd.read_excel(ficheiro, sheet_name=folha, header=None)
            primeira_linha_valida = dados.dropna(how='all').index.min()
            dados = pd.read_excel(ficheiro, sheet_name=folha, skiprows=primeira_linha_valida)
            dados["Ficheiro"] = getattr(ficheiro, 'filename', 'desconhecido.xlsx')
            dados["Folha"] = folha
            dados = dados.loc[:, ~dados.columns.str.contains("^Unnamed")]
            todos_dfs.append(dados)
        except Exception as e:
            print(f"Erro na folha {folha}: {e}")

    if todos_dfs:
        return pd.concat(todos_dfs, ignore_index=True)
    else:
        return None
