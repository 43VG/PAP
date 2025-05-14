from flask_wtf import FlaskForm  #Classe base para criar formulários seguros
from wtforms import StringField, PasswordField, SubmitField  #Tipos de campos usados nos formulários
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError  #Validadores usados para garantir que os dados são corretos
from app.models import Utilizador  #Importa o modelo de utilizador para verificar se o email já existe


class LoginForm(FlaskForm):  #Formulário usado para o login
    email = StringField("Email", validators=[DataRequired(), Email()])  #Campo de email com validação obrigatória e de formato
    senha = PasswordField("Senha", validators=[DataRequired()])  #Campo de senha obrigatório
    botao_confirm = SubmitField("Entrar")  #Botão para submeter o formulário


class CriarContaForm(FlaskForm):  #Formulário usado para criar nova conta
    nome = StringField('Nome', validators=[DataRequired()])  #Campo de nome obrigatório
    email = StringField('Email', validators=[DataRequired(), Email()])  #Campo de email obrigatório e com validação de formato
    senha = PasswordField('Senha', validators=[DataRequired()])  #Campo de senha obrigatório
    senha_confirmacao = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])  #Campo que deve ser igual à senha
    botao_confirm = SubmitField('Criar Conta')  #Botão para submeter o formulário

    def validate_email(self, email):  #Validação personalizada para garantir que o email ainda não existe na base de dados
        utilizador = Utilizador.query.filter_by(email=email.data).first()  #Procura utilizador com o mesmo email
        if utilizador:  #Se já existir um utilizador com este email
            raise ValidationError("Já existe uma conta com este email.")  #Mostra mensagem de erro
