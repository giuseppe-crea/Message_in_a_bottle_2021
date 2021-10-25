import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.core import BooleanField, StringField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname', validators=[DataRequired()])
    lastname = f.StringField('lastname', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    dateofbirth = f.DateField('dateofbirth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'dateofbirth']

 
class MessageForm(FlaskForm):
    sender_email = f.StringField(label=('Enter sender email:'), 
               validators=[DataRequired(), Email()])
    receiver_email = f.StringField(label=('Enter receiver email:'), validators=[DataRequired(), Email()])
    message = f.TextAreaField(label=('Enter message:'), validators=[DataRequired(), 
    Length(min=10, max=250, message="Message length must be  %(min)d and %(max)d characters")])
    is_draft = f.BooleanField(label=('Is draft:'))
    display = ['sender_email', 'receiver_email', 'message', 'is_draft']
