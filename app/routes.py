from flask import render_template, redirect, url_for, flash, request, Blueprint
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, CriarContaForm
from app.models import Utilizador

rotas = Blueprint('rotas', __name__)


@rotas.route("/", methods=["GET", "POST"])
def homepage():
    if current_user.is_authenticated:
        return redirect(url_for("rotas.dashboard"))  
    formLog = LoginForm()
    if formLog.validate_on_submit():
        utilizador = Utilizador.query.filter_by(email=formLog.email.data).first()
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formLog.senha.data):
            login_user(utilizador)
            return redirect(url_for("rotas.dashboard"))  
        else:
            flash("Login inválido.", "danger")
    return render_template("homepage.html", formLog=formLog)


@rotas.route("/criarconta", methods=["GET", "POST"])
def criarconta():
    form = CriarContaForm()
    if form.validate_on_submit():  
        senha_hash = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        novo_utilizador = Utilizador(nome=form.nome.data, email=form.email.data, senha=senha_hash)
        db.session.add(novo_utilizador)
        db.session.commit()
        return redirect(url_for('rotas.login'))
    return render_template("criarconta.html", formLog=form)  


@rotas.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("rotas.dashboard"))  
    formLog = LoginForm()
    if formLog.validate_on_submit():
        utilizador = Utilizador.query.filter_by(email=formLog.email.data).first()
        if utilizador and bcrypt.check_password_hash(utilizador.senha, formLog.senha.data):
            login_user(utilizador)
            return redirect(url_for("rotas.dashboard"))  
        else:
            flash("Login inválido.", "danger")
    return render_template("login.html", formLog=formLog)


@rotas.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("rotas.homepage")) 


@rotas.route("/dashboard")
@login_required  
def dashboard():
    return render_template("dashboard.html")  
