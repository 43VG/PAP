from flask import render_template, redirect, url_for, flash, request, Blueprint, session, send_file #Importa funções para mostrar páginas, redirecionar, mensagens e ler dados do formulário
from app import db, bcrypt #Importa a base de dados e o sistema de encriptação de senhas
from flask_login import login_user, logout_user, login_required, current_user #Importa funções de login, logout, proteção de rotas e acesso ao utilizador atual
from app.forms import FormularioLogin, FormularioCriarConta #Importa os formulários criados para login e criação de conta
from app.models import Utilizador #Importa o modelo de utilizador (estrutura da base de dados)
import pandas as pd #Importa pandas para manipulação de dados em tabelas
import plotly.express as px #Importa plotly para criação de gráficos 
import plotly.graph_objects as go #Adiciona import do graph_objects
import io #Biblioteca para trabalhar com ficheiros em memória
import os #Importa o módulo OS para interagir com o sistema de ficheiros (guardar uploads, criar pastas)
import json #Importa o módulo json para manipulação de dados JSON
import shutil #Importa o módulo shutil para operações de arquivos e diretórios
from .utils import obter_folhas_excel, ler_folhas_selecionadas #Importa funções que extraiem e leem os nomes das folhas de um ficheiro Excel
from werkzeug.utils import secure_filename #Função que limpa nomes de ficheiros (evita erros de segurança ao guardar ficheiros no disco)


rotas = Blueprint('rotas', __name__) #Cria um conjunto de rotas com o nome "rotas" (Blueprint permite organizar as páginas)

@rotas.route("/", methods=["GET", "POST"])
def pagina_inicial(): #Página inicial do site (login direto se já estiver autenticado)
    if current_user.is_authenticated:
        return redirect(url_for("rotas.painel"))  #Vai direto ao dashboard se já estiver logado
    formulario = FormularioLogin()  #Cria formulário de login
    if formulario.validate_on_submit():  #Se o formulário for submetido e for válido
        utilizador = Utilizador.query.filter_by(email=formulario.email.data).first()  #Procura utilizador pelo e-mail
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formulario.senha.data):  #Verifica se a senha está correta
            login_user(utilizador)  #Faz login do utilizador
            return redirect(url_for("rotas.painel"))  #Vai para o dashboard
        else:
            flash("Email ou senha incorretos. Por favor, tente novamente.", "danger")  #Mostra mensagem de erro
    return render_template("pagina_inicial.html", formulario=formulario)  #Mostra a homepage com o formulário

@rotas.route("/criarconta", methods=["GET", "POST"])
def criar_conta():
    formulario = FormularioCriarConta()  #Cria formulário de registo
    if formulario.validate_on_submit():  #Se o formulário for válido
        senha_hash = bcrypt.generate_password_hash(formulario.senha.data).decode('utf-8') #Encripta a senha
        novo_utilizador = Utilizador(
            nome=formulario.nome.data, 
            email=formulario.email.data, 
            senha=senha_hash
        )  #Cria um novo utilizador com os dados
        db.session.add(novo_utilizador)  #Adiciona à base de dados
        db.session.commit()  #Guarda na base de dados
        flash('Conta criada com sucesso! Agora pode fazer login.', 'success')  #Mensagem de sucesso
        return redirect(url_for('rotas.login'))  #Redireciona para a página de login
    return render_template("criar_conta.html", formulario=formulario)  #Mostra o formulário de criação de conta

@rotas.route("/login", methods=["GET", "POST"])
def login():
    #Página de login (igual à homepage, mas separada)
    if current_user.is_authenticated:
        return redirect(url_for("rotas.painel"))  #Se já estiver logado, vai para o dashboard
    formulario = FormularioLogin()  #Cria formulário de login
    if formulario.validate_on_submit():  #Se o formulário for válido
        utilizador = Utilizador.query.filter_by(email=formulario.email.data).first()  #Procura utilizador
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formulario.senha.data):  
            #Verifica senha
            login_user(utilizador)  #Faz login
            return redirect(url_for("rotas.painel"))  #Vai para o dashboard
        else:
            flash("Email ou senha incorretos. Por favor, tente novamente.", "danger")  #Mensagem de erro
    return render_template("login.html", formulario=formulario)  #Mostra o formulário

@rotas.route("/sair")
@login_required
def sair(): #Página para fazer logout (só acessível se estiver logado)
    logout_user()  #Termina a sessão
    return redirect(url_for("rotas.pagina_inicial"))  #Vai para a homepage

@rotas.route("/painel")
@login_required  
def painel():#Página principal protegida do utilizador
    return render_template("painel.html")  #Mostra o dashboard


PASTA_UPLOADS = "ficheiros_recebidos" #Pasta temporária onde os ficheiros vão ser guardados
os.makedirs(PASTA_UPLOADS, exist_ok=True)  #Garante que a pasta existe; se não existir, é criada

@rotas.route("/enviar_excel", methods=["POST"])
@login_required
def enviar_excel():
    folhas_por_ficheiro = {}  #Dicionário que vai guardar as folhas de cada ficheiro
    ficheiros_recebidos = request.files.getlist("ficheiros")  #Recebe a lista de ficheiros enviados pelo formulário

    if not ficheiros_recebidos:
        flash("Nenhum ficheiro foi enviado.", "danger")  #Mostra mensagem de erro se nenhum ficheiro for enviado
        return redirect(url_for("rotas.painel"))  #Redireciona de volta ao dashboard

    arquivos_invalidos = []  #Lista para guardar nomes dos arquivos inválidos
    tem_excel = False  #Flag para verificar se pelo menos um arquivo Excel foi enviado

    for ficheiro in ficheiros_recebidos:
        if ficheiro.filename.endswith((".xlsx", ".xls")):  #Verificar que é ficheiro Excel (.xlsx ou .xls)
            tem_excel = True
            nome_seguro = secure_filename(ficheiro.filename)  #Limpa o nome do ficheiro para evitar erros de segurança
            caminho = os.path.join(PASTA_UPLOADS, nome_seguro)  #Define o caminho onde o ficheiro será guardado
            ficheiro.save(caminho)  #Guarda o ficheiro localmente

            folhas = obter_folhas_excel(caminho)  #Usa função auxiliar para obter os nomes das folhas do Excel
            if folhas:  #Se conseguiu ler as folhas
                folhas_por_ficheiro[nome_seguro] = folhas  #Associa as folhas ao nome do ficheiro no dicionário
            else:  #Se não conseguiu ler as folhas
                arquivos_invalidos.append(nome_seguro)  #Adiciona à lista de inválidos
                if os.path.exists(caminho):
                    os.remove(caminho)  #Remove o arquivo inválido do sistema
        else:
            arquivos_invalidos.append(ficheiro.filename)  #Adiciona arquivos não-Excel à lista de inválidos

    if arquivos_invalidos:
        flash(f"Os seguintes arquivos não são Excel válidos: {', '.join(arquivos_invalidos)}", "warning")  #Mostra mensagem com lista de arquivos inválidos
        if not tem_excel:
            return redirect(url_for("rotas.painel"))  #Volta ao dashboard se não houver nenhum Excel válido

    if not folhas_por_ficheiro:
        flash("Nenhum arquivo Excel válido foi enviado.", "danger")  #Mensagem se nenhum Excel válido foi processado
        return redirect(url_for("rotas.painel"))  #Volta ao dashboard

    return render_template("painel.html", folhas_por_ficheiro=folhas_por_ficheiro)  #Mostra a seleção de folhas no dashboard


@rotas.route("/selecionar_folhas", methods=["POST"])
@login_required
def selecionar_folhas():
    #Limpar apenas dados específicos da sessão em vez de toda a sessão
    chaves_sessao_manter = ['_user_id', '_fresh']
    dados_sessao_manter = {chave: session[chave] for chave in chaves_sessao_manter if chave in session}
    
    ficheiros_nomes = request.form.getlist("ficheiros_nome")
    tem_folhas_selecionadas = False  #Flag para verificar se alguma folha foi selecionada
    
    #Verificar se pelo menos uma folha foi selecionada
    for nome in ficheiros_nomes:
        folhas_escolhidas = request.form.getlist(f"selecionadas_{nome}")
        if folhas_escolhidas:
            tem_folhas_selecionadas = True
            break
    
    if not tem_folhas_selecionadas:
        flash("Por favor, selecione pelo menos uma folha para continuar.", "warning")  #Mensagem de aviso
        #Recuperar informações das folhas para reexibir a página
        folhas_por_ficheiro = {}
        for nome in ficheiros_nomes:
            caminho = os.path.join(PASTA_UPLOADS, secure_filename(nome))
            folhas = obter_folhas_excel(caminho)
            folhas_por_ficheiro[nome] = folhas
        return render_template("painel.html", folhas_por_ficheiro=folhas_por_ficheiro)
    
    #Se chegou aqui, tem folhas selecionadas, então limpa a sessão e continua
    session.clear()
    session.update(dados_sessao_manter)
    
    dados_finais = []

    for nome in ficheiros_nomes:
        folhas_escolhidas = request.form.getlist(f"selecionadas_{nome}")
        caminho = os.path.join(PASTA_UPLOADS, secure_filename(nome))

        if folhas_escolhidas:
            df = ler_folhas_selecionadas(caminho, folhas_escolhidas)
            if df is not None:
                #Garantir que os nomes das colunas estão normalizados
                df.columns = df.columns.str.strip().str.replace(' ', '_')
                dados_finais.append(df)            
        else:
            flash("Nenhuma folha foi selecionada.", "warning")
            return redirect(url_for("rotas.painel"))
    
    if dados_finais:
        df_total = pd.concat(dados_finais, ignore_index=True)
        
        #Debug: mostrar estado dos dados antes de processar
        print("\nColunas antes do processamento:", df_total.columns.tolist())
        
        #Identificar colunas numéricas e de texto
        colunas_invalidas = ["Ficheiro", "Folha"]
        df_graficos = df_total.drop(columns=[col for col in colunas_invalidas if col in df_total.columns])

        #Forçar a detecção correta dos tipos de dados
        for coluna in df_graficos.columns:
            #Converter datas para o formato correto
            if 'Data' in coluna:
                try:
                    df_graficos[coluna] = pd.to_datetime(df_graficos[coluna])
                except:
                    pass
            #Converter valores numéricos
            elif df_graficos[coluna].dtype == 'object':
                try:
                    df_graficos[coluna] = pd.to_numeric(df_graficos[coluna].str.replace(',', '.'))
                except:
                    pass
        
        #Identificar tipos de colunas para o gráfico
        colunas_numericas = df_graficos.select_dtypes(include=['int64', 'float64']).columns.tolist()
        colunas_texto = df_graficos.select_dtypes(include=['object', 'datetime64[ns]']).columns.tolist()
        
        #Debug: mostrar estado final dos dados
        print("\nColunas numéricas:", colunas_numericas)
        print("Colunas texto:", colunas_texto)
        
        #Converter datas para string antes de salvar na sessão
        for coluna in df_graficos.columns:
            if pd.api.types.is_datetime64_any_dtype(df_graficos[coluna]):
                df_graficos[coluna] = df_graficos[coluna].dt.strftime('%Y-%m-%d')
        
        #Guardar os dados e tipos na sessão
        session['dados_excel'] = df_graficos.to_json(orient='records')
        session['colunas_numericas'] = colunas_numericas
        session['colunas_texto'] = colunas_texto
        flash("Dados recebidos com sucesso!", "success")
        
        tabela_preview = df_graficos.to_html(classes='table table-striped', index=False)
        return render_template("painel.html", 
                            folhas_por_ficheiro=None, 
                            preview_html=tabela_preview,
                            colunas_numericas=colunas_numericas,
                            colunas_texto=colunas_texto)
    else:
        flash("Erro ao ler os dados selecionados.", "danger")
        return redirect(url_for("rotas.painel"))

PASTA_GRAFICOS = "graficos_temp"
os.makedirs(PASTA_GRAFICOS, exist_ok=True)

def limpar_pasta_graficos():
    """Limpa a pasta de gráficos temporários"""
    if os.path.exists(PASTA_GRAFICOS):
        shutil.rmtree(PASTA_GRAFICOS)
        os.makedirs(PASTA_GRAFICOS)

@rotas.route("/gerar_grafico", methods=["POST"])
@login_required
def gerar_grafico():
    if 'dados_excel' not in session:
        flash("Nenhum dado disponível. Por favor, carregue um arquivo Excel.", "danger")
        return redirect(url_for("rotas.painel"))

    #Recuperar dados e tipos da sessão
    df = pd.read_json(io.StringIO(session['dados_excel']))
    colunas_numericas = session.get('colunas_numericas', [])
    colunas_texto = session.get('colunas_texto', [])
    
    #Garantir que os nomes das colunas estão normalizados
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    #Debug: imprimir colunas disponíveis
    print("Colunas no DataFrame:", df.columns.tolist())
    
    #Inicializar ou resetar contadores e listas se necessário
    if 'contador_graficos' not in session:
        session['contador_graficos'] = 0
    if 'lista_graficos' not in session:
        session['lista_graficos'] = []
    
    #Obter parâmetros do formulário
    coluna_x = request.form.get('coluna_x')
    coluna_y = request.form.get('coluna_y')
    tipos_graficos = request.form.getlist('tipos_graficos')

    print(f"Coluna X selecionada: {coluna_x}")
    print(f"Coluna Y selecionada: {coluna_y}")

    if not tipos_graficos:
        flash("Por favor, selecione pelo menos um tipo de gráfico para continuar.", "warning")
        tabela_preview = df.to_html(classes='table table-striped', index=False)
        return render_template("painel.html", 
                            preview_html=tabela_preview,
                            colunas_numericas=colunas_numericas,
                            colunas_texto=colunas_texto)

    #Verificar se as colunas existem no DataFrame
    if coluna_x not in df.columns:
        flash(f"Coluna '{coluna_x}' não encontrada. Colunas disponíveis: {', '.join(df.columns)}", "danger")
        return redirect(url_for("rotas.painel"))
    if coluna_y not in df.columns:
        flash(f"Coluna '{coluna_y}' não encontrada. Colunas disponíveis: {', '.join(df.columns)}", "danger")
        return redirect(url_for("rotas.painel"))

    #Converter datas de volta para datetime se necessário
    if 'Data' in coluna_x:
        df[coluna_x] = pd.to_datetime(df[coluna_x])
        df = df.sort_values(coluna_x)

    #Mover gráficos recentes para anteriores
    if 'graficos_recentes' in session:
        for grafico_id in session['graficos_recentes']:
            if grafico_id not in session.get('graficos_anteriores', []):
                if 'graficos_anteriores' not in session:
                    session['graficos_anteriores'] = []
                session['graficos_anteriores'].append(grafico_id)

    #Gerar gráficos
    graficos = {}
    session['graficos_recentes'] = []

    for tipo in tipos_graficos:
        session['contador_graficos'] += 1
        if tipo == "Barras":
            fig = px.bar(df, x=coluna_x, y=coluna_y)
        elif tipo == "Linhas":
            df_agrupado = df.groupby(coluna_x, as_index=False)[coluna_y].sum()
            fig = px.line(df_agrupado, x=coluna_x, y=coluna_y)
        elif tipo == "Pizza":
            fig = px.pie(df, names=coluna_x, values=coluna_y)

        #Configurar layout do gráfico
        fig.update_layout(
            width=800,
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        #Gerar ID único para o gráfico
        grafico_id = f"{tipo}_{session['contador_graficos']}"
        
        #Salvar o gráfico em arquivo
        caminho_grafico = os.path.join(PASTA_GRAFICOS, f"{grafico_id}.json")
        with open(caminho_grafico, 'w') as f:
            json.dump(fig.to_json(), f)
        
        #Converter para HTML e salvar apenas metadados na sessão
        html = fig.to_html(full_html=False, include_plotlyjs=True)
        graficos[grafico_id] = {
            'html': html,
            'tipo': tipo,
            'coluna_x': coluna_x,
            'coluna_y': coluna_y
        }
        
        #Adicionar à lista de gráficos e gráficos recentes
        session['lista_graficos'].append(grafico_id)
        session['graficos_recentes'].append(grafico_id)
        session.modified = True

    tabela_preview = df.to_html(classes='table table-striped', index=False)

    #Preparar gráficos anteriores
    graficos_anteriores = {}
    for k in session.get('graficos_anteriores', []):
        caminho_grafico = os.path.join(PASTA_GRAFICOS, f"{k}.json")
        if os.path.exists(caminho_grafico):
            with open(caminho_grafico, 'r') as f:
                dados_fig = json.load(f)
                fig = go.Figure(data=go.Figure(json.loads(dados_fig)).data)
                fig.update_layout(
                    width=800,
                    height=500,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                graficos_anteriores[k] = fig.to_html(full_html=False, include_plotlyjs=True)

    return render_template("painel.html",
                         preview_html=tabela_preview,
                         graficos=graficos,
                         graficos_anteriores=graficos_anteriores,
                         colunas_numericas=colunas_numericas,
                         colunas_texto=colunas_texto)

@rotas.route("/exportar_grafico/<grafico_id>/<formato>")
@login_required
def exportar_grafico(grafico_id, formato):
    import base64  #Import local para uso específico
    caminho_grafico = os.path.join(PASTA_GRAFICOS, f"{grafico_id}.json")
    if not os.path.exists(caminho_grafico):
        flash("Gráfico não encontrado. Por favor, gere o gráfico novamente.", "danger")
        return redirect(url_for("rotas.painel"))

    #Recuperar o gráfico do arquivo
    with open(caminho_grafico, 'r') as f:
        dados_fig = json.load(f)
        fig = go.Figure(data=go.Figure(json.loads(dados_fig)).data)
        fig.update_layout(
            width=800,
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
    
    #Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    if formato == 'png':
        fig.write_image(buffer, format='png')
        mimetype = 'image/png'
        nome_arquivo = f'grafico_{grafico_id}.png'
    elif formato == 'pdf':
        fig.write_image(buffer, format='pdf')
        mimetype = 'application/pdf'
        nome_arquivo = f'grafico_{grafico_id}.pdf'
    else:
        flash("Formato de exportação inválido.", "danger")
        return redirect(url_for("rotas.painel"))

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype=mimetype,
        as_attachment=True,
        download_name=nome_arquivo
    )

@rotas.route("/limpar_graficos", methods=["POST"])
@login_required
def limpar_graficos():
    #Limpar todos os gráficos da sessão e arquivos
    if 'lista_graficos' in session:
        session.pop('lista_graficos', None)
    
    #Limpar as listas de gráficos recentes e anteriores
    session.pop('graficos_recentes', None)
    session.pop('graficos_anteriores', None)
    session.pop('contador_graficos', None)
    
    #Limpar arquivos de gráficos
    limpar_pasta_graficos()
    
    flash("Todos os gráficos foram limpos.", "success")
    return redirect(url_for("rotas.painel"))

@rotas.route("/voltar_selecao_folhas", methods=["POST"])
@login_required
def voltar_selecao_folhas():
    #Preservar apenas os dados dos arquivos e folhas
    ficheiros_nomes = []
    folhas_por_ficheiro = {}
    
    #Recuperar os arquivos da pasta de uploads
    if os.path.exists(PASTA_UPLOADS):
        for arquivo in os.listdir(PASTA_UPLOADS):
            if arquivo.endswith(('.xlsx', '.xls')):
                ficheiros_nomes.append(arquivo)
                caminho = os.path.join(PASTA_UPLOADS, arquivo)
                folhas = obter_folhas_excel(caminho)
                folhas_por_ficheiro[arquivo] = folhas
    
    return render_template("painel.html", folhas_por_ficheiro=folhas_por_ficheiro)

@rotas.route("/voltar_upload", methods=["POST"])
@login_required
def voltar_upload():
    #Limpar arquivos temporários
    if os.path.exists(PASTA_UPLOADS):
        for arquivo in os.listdir(PASTA_UPLOADS):
            caminho = os.path.join(PASTA_UPLOADS, arquivo)
            try:
                if os.path.isfile(caminho):
                    os.remove(caminho)
            except Exception as e:
                print(f"Erro ao remover arquivo {arquivo}: {e}")
    
    return render_template("painel.html")