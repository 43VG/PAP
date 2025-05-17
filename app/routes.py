from flask import render_template, redirect, url_for, flash, request, Blueprint #Importa funções para mostrar páginas, redirecionar, mensagens e ler dados do formulário
from app import db, bcrypt #Importa a base de dados e o sistema de encriptação de senhas
from flask_login import login_user, logout_user, login_required, current_user #Importa funções de login, logout, proteção de rotas e acesso ao utilizador atual
from app.forms import LoginForm, CriarContaForm #Importa os formulários criados para login e criação de conta
from app.models import Utilizador #Importa o modelo de utilizador (estrutura da base de dados)
import pandas as pd
import plotly.express as px
import base64
import io

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

@rotas.route("/upload", methods=["POST"])
@login_required
def upload_excel():
    ficheiros = request.files.getlist("ficheiros_excel")  # Lê os ficheiros enviados
    graficos = []  # Lista para guardar os gráficos gerados

    for ficheiro in ficheiros:
        try:
            # Lê todas as folhas do ficheiro Excel como dicionário
            folhas = pd.read_excel(ficheiro, sheet_name=None)

            for nome_folha, df in folhas.items():
                df = df.dropna(how='all')  # Remove linhas completamente vazias

                # Deteta colunas numéricas automaticamente
                colunas_numericas = df.select_dtypes(include=['number']).columns
                if len(colunas_numericas) == 0:
                    continue

                for col in colunas_numericas:
                    fig = px.bar(df, y=col, title=f"{ficheiro.filename} - {nome_folha} - {col}")
                    buffer = io.BytesIO()
                    fig.write_image(buffer, format="png")
                    buffer.seek(0)
                    imagem_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                    graficos.append(imagem_base64)

        except Exception as e:
            flash(f"Erro ao processar {ficheiro.filename}: {str(e)}", "danger")

    return render_template("dashboard.html", graficos=graficos)