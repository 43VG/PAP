from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "rotas.homepage"
login_manager.login_message_category = "info"

def criar_app():
    print("A criar app...")
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "chave_super_secreta_123"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///basedados.db"

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes import rotas
    app.register_blueprint(rotas)

    print("App criada com sucesso!")
    return app
