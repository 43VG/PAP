from app import db, login_manager  #Importa a base de dados e o sistema de login da app
from flask_login import UserMixin  #Classe que adiciona funcionalidades essenciais ao modelo de utilizador (como is_authenticated)

@login_manager.user_loader
def load_user(user_id):  #Esta função carrega o utilizador com base no ID (obrigatória para o Flask-Login)
    return Utilizador.query.get(int(user_id))  #Vai à base de dados buscar o utilizador com o ID indicado


class Utilizador(db.Model, UserMixin):  #Criação da tabela 'utilizador' na base de dados, com suporte a login
    id = db.Column(db.Integer, primary_key=True)  #Coluna 'id', chave primária e valor único
    nome = db.Column(db.String(100), nullable=False)  #Coluna 'nome', texto obrigatório
    email = db.Column(db.String(150), unique=True, nullable=False)  #Coluna 'email', deve ser único e obrigatório
    senha = db.Column(db.String(200), nullable=False)  #Coluna 'senha', onde é guardada a senha encriptada

    def __repr__(self):  #Função que define o formato do objeto ao imprimir (para depuração)
        return f"Utilizador('{self.nome}', '{self.email}')"  #Mostra o nome e email do utilizador
