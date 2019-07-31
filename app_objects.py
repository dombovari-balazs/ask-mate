from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo


RECAPTCHA_PUBLIC_KEY = 'csocsike'
RECAPTCHA_PRIVATE_KEY = 'pocsike'


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('confirm', validators=[InputRequired()])
    submit = SubmitField('Register')


