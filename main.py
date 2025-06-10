from app import criar_app, db  #Criar a aplicação Flask e base de dados 
from app.models import Utilizador  #Importa o modelo de dados 'Utilizador' de models.py

app = criar_app()  #Cria e configura a aplicação Flask através da função definida em __init__.py

with app.app_context():  #Cria um contexto da aplicação (necessário para aceder à base de dados fora das rotas)
    db.create_all()  #Cria as tabelas da base de dados com base nos modelos definidos (ex: Utilizador)

if __name__ == "__main__":  #Verifica se o ficheiro está a ser executado diretamente 
    app.run(debug=False)  #Inicia o servidor Flask 

with app.app_context():  #Abre novamente o contexto da app
    print(Utilizador.query.all())  #Mostra no terminal todos os utilizadores registados na base de dados (para depuração)
