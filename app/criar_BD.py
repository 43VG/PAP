from app import app, db #Importa a base de dados e o sistema de encriptação de senhas
from app.models import Utilizador  #Importa o modelo de utilizador (estrutura da base de dados)

# Criar a base de dados com as tabelas do models.py
with app.app_context(): #Executa dentro do contexto da aplicação Flask
    db.create_all() #Cria todas as tabelas definidas em models.py
    print("Base de dados criada com sucesso!") #Mensagem de depuração
