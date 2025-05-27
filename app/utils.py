import pandas as pd  #Para manipulação de dados em tabelas
import os 

#Devolve os nomes das folhas do Excel
def obter_folhas_excel(ficheiro):
    try:
        #Abre o ficheiro Excel 
        excel_file = pd.ExcelFile(ficheiro)
        #Devolve a lista de nomes das folhas
        return excel_file.sheet_names
    except Exception as e:
        #Mostra erro no terminal (depuração)
        print(f"Erro ao obter folhas: {e}")
        return []

#Lê apenas as folhas escolhidas e devolve o DataFrame final
def ler_folhas_selecionadas(ficheiro, folhas_escolhidas):
    #Lista onde vão ser guardados todos os DataFrames lidos
    todos_dfs = []
    for folha in folhas_escolhidas:
        try:
            #Lê a folha sem assumir cabeçalho, para encontrar onde começam os dados
            dados = pd.read_excel(ficheiro, sheet_name=folha, header=None)
            
            #Identifica a primeira linha com conteúdo (ignora linhas totalmente vazias)
            primeira_linha_valida = dados.dropna(how='all').index.min()
            
            #Lê novamente a folha, agora a partir da linha com dados reais
            dados = pd.read_excel(ficheiro, sheet_name=folha, skiprows=primeira_linha_valida)
            
            #Normaliza os nomes das colunas
            dados.columns = dados.columns.str.strip().str.replace(' ', '_')
            
            #Adiciona informações do arquivo
            dados["Ficheiro"] = os.path.basename(ficheiro)
            dados["Folha"] = folha
            
            #Remove colunas automáticas sem nome (geradas pelo Excel)
            dados = dados.loc[:, ~dados.columns.str.contains("^Unnamed")]
            
            #Debug: mostra as colunas sendo lidas
            print(f"Colunas lidas do arquivo {os.path.basename(ficheiro)}, folha {folha}:", dados.columns.tolist())
            
            todos_dfs.append(dados)

        except Exception as e:
            print(f"Erro na folha {folha}: {e}")

    if todos_dfs:
        #Combina todos os DataFrames
        df_final = pd.concat(todos_dfs, ignore_index=True)
        
        #Debug: mostra as colunas finais
        print("Colunas finais após concatenação:", df_final.columns.tolist())
        
        return df_final
    else:
        return None