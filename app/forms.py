from flask_wtf import FlaskForm  #Classe base para criar formulários seguros
from wtforms import StringField, PasswordField, SubmitField  #Tipos de campos usados nos formulários
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError  #Validadores usados para garantir que os dados são corretos
from app.models import Utilizador  #Importa o modelo de utilizador para verificar se o email já existe


class FormularioLogin(FlaskForm):  #Formulário usado para o login
    email = StringField('Email', validators=[DataRequired(), Email()])  #Campo de email com validação obrigatória e de formato
    senha = PasswordField('Senha', validators=[DataRequired()])  #Campo de senha obrigatório
    submeter = SubmitField('Entrar')  #Botão para submeter o formulário


class FormularioCriarConta(FlaskForm):  #Formulário usado para criar nova conta
    nome = StringField('Nome', validators=[DataRequired(message="Por favor, insira o seu nome."), Length(min=2, max=20, message="O nome deve ter entre 2 e 20 caracteres.")])
    email = StringField('Email', validators=[DataRequired(message="Por favor, insira o seu email."), Email(message="Por favor, insira um endereço de email válido.")])
    senha = PasswordField('Senha', validators=[DataRequired(message="Por favor, insira uma senha."), Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(message="Por favor, confirme sua senha."), EqualTo('senha', message="As senhas não coincidem.")])
    submeter = SubmitField('Criar Conta')

    def validate_email(self, email):  #Validação para garantir que o email ainda não existe na base de dados
        utilizador = Utilizador.query.filter_by(email=email.data).first()  #Procura utilizador com o mesmo email
        if utilizador:  #Se já existir um utilizador com este email
            raise ValidationError('Este email já está registado. Por favor, escolha outro.')  #Mostra mensagem de erro
