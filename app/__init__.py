from flask import Flask  #Flask para criar a aplicação web
from flask_sqlalchemy import SQLAlchemy  #SQLAlchemy para gerir a base de dados
from flask_bcrypt import Bcrypt  #Bcrypt para encriptar senhas
from flask_login import LoginManager  #Importa LoginManager para gerir sessões de utilizadores (login/logout)
import os  #Para aceder a variáveis de ambiente
from dotenv import load_dotenv  #Para carregar o ficheiro .env

#Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

db = SQLAlchemy()  #Objeto da base de dados
bcrypt = Bcrypt()  #Objeto para encriptação de senhas
login_manager = LoginManager()  #Gestor de sessões de utilizadores
login_manager.login_view = "rotas.pagina_inicial"  #Define a página para onde o utilizador será redirecionado se não estiver autenticado
login_manager.login_message_category = "info"  #Define o estilo da mensagem flash (aviso) que aparece quando o login é exigido

def criar_app():  #Função que cria e configura a aplicação Flask
    print("A criar app...")  #Mensagem de depuração no terminal

    app = Flask(__name__)  #Cria a instância principal da aplicação
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "97G8MSGSIUDFHA68S")  #Define a chave secreta (usada para sessões e segurança)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///basedados.db")  #Define o caminho da base de dados SQLite

    db.init_app(app)  #Liga o SQLAlchemy à aplicação Flask
    bcrypt.init_app(app)  #Liga o Bcrypt à aplicação Flask
    login_manager.init_app(app)  #Liga o LoginManager à aplicação Flask

    from app.routes import rotas  #Importa as rotas definidas no ficheiro routes.py
    app.register_blueprint(rotas)  #Blueprint regista rotas 

    print("App criada com sucesso!")  #Mensagem de depuração
    return app  #Devolve a aplicação pronta a ser usada
