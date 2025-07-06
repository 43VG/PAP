# Instruções para Deploy

## Configuração Local

1. **Criar ficheiro `.env` na raiz do projeto:**
```
SECRET_KEY=97G8MSGSIUDFHA68S
DATABASE_URL=sqlite:///basedados.db
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

## Deploy Online

### Render (Recomendado)

1. **Criar conta no Render.com**
2. **Conectar ao GitHub**
3. **Criar novo Web Service**
4. **Configurar variáveis de ambiente no painel do Render:**
   - `SECRET_KEY`: (chave secreta nova)
   - `DATABASE_URL`: (URL da base de dados PostgreSQL fornecida pelo Render)

### Railway

1. **Criar conta no Railway.app**
2. **Conectar ao GitHub**
3. **Deploy automático**
4. **Configurar variáveis de ambiente no painel**

### Heroku

1. **Criar conta no Heroku.com**
2. **Instalar Heroku CLI**
3. **Configurar variáveis de ambiente:**
```bash
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set DATABASE_URL=sua-url-postgresql
```

## Ficheiros Necessários

- `Procfile` (para Heroku/Railway):
```
web: gunicorn main:app
```

- Adicionar `gunicorn` aos requirements.txt se necessário 