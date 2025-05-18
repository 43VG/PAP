import pandas as pd  #Para manipulação de dados em tabelas
import os 


def obter_folhas_excel(ficheiro):
    """Devolve os nomes das folhas do Excel"""
    try:
        excel_file = pd.ExcelFile(ficheiro)  #Abre o ficheiro Excel 
        return excel_file.sheet_names        #Devolve a lista de nomes das folhas
    except Exception as e:
        print(f"Erro ao obter folhas: {e}")  #Mostra erro no terminal (depuração)
        return []

def ler_folhas_selecionadas(ficheiro, folhas_escolhidas):
    """Lê apenas as folhas escolhidas e devolve o DataFrame final"""
    todos_dfs = []  #Lista onde vão ser guardados todos os DataFrames lidos

    for folha in folhas_escolhidas:
        try:
            dados = pd.read_excel(ficheiro, sheet_name=folha, header=None) #Lê a folha sem assumir cabeçalho, para encontrar onde começam os dados
            primeira_linha_valida = dados.dropna(how='all').index.min() #Identifica a primeira linha com conteúdo (ignora linhas totalmente vazias)
            dados = pd.read_excel(ficheiro, sheet_name=folha, skiprows=primeira_linha_valida) #Lê novamente a folha, agora a partir da linha com dados reais
            dados["Ficheiro"] = os.path.basename(ficheiro)  #Guarda o nome do ficheiro a partir do caminho
            dados["Folha"] = folha
            dados = dados.loc[:, ~dados.columns.str.contains("^Unnamed")] #Remove colunas automáticas sem nome (geradas pelo Excel)
            todos_dfs.append(dados) #Guarda o DataFrame na lista

        except Exception as e:
            print(f"Erro na folha {folha}: {e}")  #Mostra erro se a leitura falhar

    if todos_dfs: #Junta todos os DataFrames lidos num só
        return pd.concat(todos_dfs, ignore_index=True)
    else:
        return None  #Se não houver dados válidos