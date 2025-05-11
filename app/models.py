from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Utilizador.query.get(int(user_id))

# modelo de utilizador
class Utilizador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Utilizador('{self.nome}', '{self.email}')"
