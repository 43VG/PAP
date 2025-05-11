from app import criar_app, db
from app.models import Utilizador

app = criar_app()


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

with app.app_context():
    print(Utilizador.query.all()) 