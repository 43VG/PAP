from flask import render_template, redirect, url_for, flash, request, Blueprint, session, send_file #Importa funções para mostrar páginas, redirecionar, mensagens e ler dados do formulário
from app import db, bcrypt #Importa a base de dados e o sistema de encriptação de senhas
from flask_login import login_user, logout_user, login_required, current_user #Importa funções de login, logout, proteção de rotas e acesso ao utilizador atual
from app.forms import LoginForm, CriarContaForm #Importa os formulários criados para login e criação de conta
from app.models import Utilizador #Importa o modelo de utilizador (estrutura da base de dados)
import pandas as pd #Importa pandas para manipulação de dados em tabelas
import plotly.express as px #Importa plotly para criação de gráficos 
import base64 #Permite codificar imagens em base64 para exportar
import io #Biblioteca para trabalhar com ficheiros em memória
import os #Importa o módulo OS para interagir com o sistema de ficheiros (guardar uploads, criar pastas)
from .utils import obter_folhas_excel, ler_folhas_selecionadas #Importa funções que extraiem e leem os nomes das folhas de um ficheiro Excel
from werkzeug.utils import secure_filename #Função que limpa nomes de ficheiros (evita erros de segurança ao guardar ficheiros no disco)


rotas = Blueprint('rotas', __name__) #Cria um conjunto de rotas com o nome "rotas" (Blueprint permite organizar as páginas)

@rotas.route("/", methods=["GET", "POST"])
def homepage(): #Página inicial do site (login direto se já estiver autenticado)
    if current_user.is_authenticated:
        return redirect(url_for("rotas.dashboard"))  #Vai direto ao dashboard se já estiver logado
    formLog = LoginForm()  #Cria formulário de login
    if formLog.validate_on_submit():  #Se o formulário for submetido e for válido
        utilizador = Utilizador.query.filter_by(email=formLog.email.data).first()  #Procura utilizador pelo e-mail
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formLog.senha.data):  #Verifica se a senha está correta
            login_user(utilizador)  #Faz login do utilizador
            return redirect(url_for("rotas.dashboard"))  #Vai para o dashboard
        else:
            flash("Login inválido.", "danger")  #Mostra mensagem de erro
    return render_template("homepage.html", formLog=formLog)  #Mostra a homepage com o formulário

@rotas.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form = CriarContaForm()  #Cria formulário de registo
    if form.validate_on_submit():  #Se o formulário for válido
        senha_hash = bcrypt.generate_password_hash(form.senha.data).decode('utf-8') #Encripta a senha
        novo_utilizador = Utilizador(
            nome=form.nome.data, 
            email=form.email.data, 
            senha=senha_hash
        )  #Cria um novo utilizador com os dados
        db.session.add(novo_utilizador)  #Adiciona à base de dados
        db.session.commit()  #Guarda na base de dados
        return redirect(url_for('rotas.login'))  #Redireciona para a página de login
    return render_template("criarconta.html", formLog=form)  #Mostra o formulário de criação de conta

@rotas.route("/login", methods=["GET", "POST"])
def login():
    #Página de login (igual à homepage, mas separada)
    if current_user.is_authenticated:
        return redirect(url_for("rotas.dashboard"))  #Se já estiver logado, vai para o dashboard
    formLog = LoginForm()  #Cria formulário de login
    if formLog.validate_on_submit():  #Se o formulário for válido
        utilizador = Utilizador.query.filter_by(email=formLog.email.data).first()  #Procura utilizador
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formLog.senha.data):  
            #Verifica senha
            login_user(utilizador)  #Faz login
            return redirect(url_for("rotas.dashboard"))  #Vai para o dashboard
        else:
            flash("Login inválido.", "danger")  #Mensagem de erro
    return render_template("login.html", formLog=formLog)  #Mostra o formulário

@rotas.route("/logout")
@login_required
def logout(): #Página para fazer logout (só acessível se estiver logado)
    logout_user()  #Termina a sessão
    return redirect(url_for("rotas.homepage"))  #Vai para a homepage

@rotas.route("/dashboard")
@login_required  
def dashboard():#Página principal protegida do utilizador
    return render_template("dashboard.html")  #Mostra o dashboard


UPLOAD_FOLDER = "ficheiros_recebidos" #Pasta temporária onde os ficheiros vão ser guardados
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  #Garante que a pasta existe; se não existir, é criada

@rotas.route("/upload_excel", methods=["POST"])
@login_required
def upload_excel():
    folhas_por_ficheiro = {}  #Dicionário que vai guardar as folhas de cada ficheiro
    ficheiros_recebidos = request.files.getlist("ficheiros")  #Recebe a lista de ficheiros enviados pelo formulário

    if not ficheiros_recebidos:
        flash("Nenhum ficheiro foi enviado.", "danger")  #Mostra mensagem de erro se nenhum ficheiro for enviado
        return redirect(url_for("rotas.dashboard"))  #Redireciona de volta ao dashboard

    for ficheiro in ficheiros_recebidos:
        if ficheiro.filename.endswith(".xlsx"): #Verificar que é ficheiro Excel
            nome_seguro = secure_filename(ficheiro.filename)  #Limpa o nome do ficheiro para evitar erros de segurança
            caminho = os.path.join(UPLOAD_FOLDER, nome_seguro)  #Define o caminho onde o ficheiro será guardado
            ficheiro.save(caminho)  #Guarda o ficheiro localmente

            folhas = obter_folhas_excel(caminho)  #Usa função auxiliar para obter os nomes das folhas do Excel
            folhas_por_ficheiro[nome_seguro] = folhas  #Associa as folhas ao nome do ficheiro no dicionário

    return render_template("dashboard.html", folhas_por_ficheiro=folhas_por_ficheiro)  #Mostra a seleção de folhas no dashboard


@rotas.route("/selecionar_folhas", methods=["POST"])
@login_required
def selecionar_folhas():
    ficheiros_nomes = request.form.getlist("ficheiros_nome")
    dados_finais = []

    for nome in ficheiros_nomes:
        folhas_escolhidas = request.form.getlist(f"selecionadas_{nome}")
        caminho = os.path.join(UPLOAD_FOLDER, secure_filename(nome))

        if folhas_escolhidas:
            df = ler_folhas_selecionadas(caminho, folhas_escolhidas)
            if df is not None:
                dados_finais.append(df)            
        else:
            flash("Nenhuma folha foi selecionada.", "warning")
            return redirect(url_for("rotas.dashboard"))
    
    if dados_finais:
        df_total = pd.concat(dados_finais, ignore_index=True)
        session['dados_excel'] = df_total.to_json(orient='records')
        flash("Dados recebidos com sucesso!", "success")
        
        #Identificar colunas numéricas e de texto
        colunas_invalidas = ["Ficheiro", "Folha"]
        df_graficos = df_total.drop(columns=[col for col in colunas_invalidas if col in df_total.columns])
        colunas_numericas = df_graficos.select_dtypes(include='number').columns.tolist()
        colunas_texto = df_graficos.select_dtypes(include='object').columns.tolist()
        
        tabela_preview = df_total.to_html(classes='table table-striped', index=False)
        return render_template("dashboard.html", 
                            folhas_por_ficheiro=None, 
                            preview_html=tabela_preview,
                            colunas_numericas=colunas_numericas,
                            colunas_texto=colunas_texto)
    else:
        flash("Erro ao ler os dados selecionados.", "danger")
        return redirect(url_for("rotas.dashboard"))

@rotas.route("/gerar_grafico", methods=["POST"])
@login_required
def gerar_grafico():
    if 'dados_excel' not in session:
        flash("Nenhum dado disponível. Por favor, carregue um arquivo Excel.", "danger")
        return redirect(url_for("rotas.dashboard"))

    #Recuperar dados da sessão
    df = pd.read_json(session['dados_excel'])
    
    #Obter parâmetros do formulário
    coluna_x = request.form.get('coluna_x')
    coluna_y = request.form.get('coluna_y')
    tipos_graficos = request.form.getlist('tipos_graficos')

    if not tipos_graficos:
        flash("Selecione pelo menos um tipo de gráfico.", "warning")
        return redirect(url_for("rotas.dashboard"))

    #Gerar gráficos
    graficos = {}
    for tipo in tipos_graficos:
        if tipo == "Barras":
            fig = px.bar(df, x=coluna_x, y=coluna_y, title=f"Gráfico de Barras: {coluna_y} por {coluna_x}")
        elif tipo == "Linhas":
            df_agrupado = df.groupby(coluna_x, as_index=False)[coluna_y].sum()
            fig = px.line(df_agrupado, x=coluna_x, y=coluna_y, title=f"Gráfico de Linhas: {coluna_y} por {coluna_x}")
        elif tipo == "Pizza":
            fig = px.pie(df, names=coluna_x, values=coluna_y, title=f"Gráfico de Pizza: {coluna_y} por {coluna_x}")

        #Configurar layout do gráfico
        fig.update_layout(
            width=800,
            height=500,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        #Guardar o gráfico na sessão para exportação
        session[f'grafico_{tipo}'] = fig.to_json()
        
        #Converter para HTML
        graficos[tipo] = fig.to_html(full_html=False)

    #Prévisualização 
    df_graficos = df.drop(columns=["Ficheiro", "Folha"] if "Ficheiro" in df.columns else [])
    colunas_numericas = df_graficos.select_dtypes(include='number').columns.tolist()
    colunas_texto = df_graficos.select_dtypes(include='object').columns.tolist()
    tabela_preview = df.to_html(classes='table table-striped', index=False)

    return render_template("dashboard.html",
                         preview_html=tabela_preview,
                         graficos=graficos,
                         colunas_numericas=colunas_numericas,
                         colunas_texto=colunas_texto)

@rotas.route("/exportar_grafico/<tipo>/<formato>")
@login_required
def exportar_grafico(tipo, formato):
    if f'grafico_{tipo}' not in session:
        flash("Gráfico não encontrado. Por favor, gere o gráfico novamente.", "danger")
        return redirect(url_for("rotas.dashboard"))

    #Recuperar o gráfico da sessão
    fig = px.Figure().from_json(session[f'grafico_{tipo}'])
    
    #Criar buffer para o arquivo
    buffer = io.BytesIO()
    
    if formato == 'png':
        fig.write_image(buffer, format='png')
        mimetype = 'image/png'
        filename = f'grafico_{tipo.lower()}.png'
    elif formato == 'pdf':
        fig.write_image(buffer, format='pdf')
        mimetype = 'application/pdf'
        filename = f'grafico_{tipo.lower()}.pdf'
    else:
        flash("Formato de exportação inválido.", "danger")
        return redirect(url_for("rotas.dashboard"))

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )