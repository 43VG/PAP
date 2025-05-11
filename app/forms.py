from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import Utilizador  


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    botao_confirm = SubmitField("Entrar")

class CriarContaForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    senha_confirmacao = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])  
    botao_confirm = SubmitField('Criar Conta')

    def validate_email(self, email):
        utilizador = Utilizador.query.filter_by(email=email.data).first()
        if utilizador:
            raise ValidationError("Já existe uma conta com este email.")
