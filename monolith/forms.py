from datetime import datetime

import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import StopValidation, InputRequired, Length
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.widgets import TextArea
from wtforms import BooleanField

class TimeValidator(object):
    field_flags = ('required',)

    def __init__(self, startdate=datetime.now(), message=None):
        self.startdate = startdate
        if not message:
            message = "You can't set a delivery date earlier than " + startdate.strftime("%m/%d/%Y, %H:%M:%S") + "!"
        self.message = message

    def __call__(self, form, field):
        if field.data < self.startdate:
            field.errors[:] = []
            raise StopValidation(self.message)


time_validator = TimeValidator

class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[InputRequired()])
    password = f.PasswordField('password', validators=[InputRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[InputRequired()])
    firstname = f.StringField('firstname', validators=[InputRequired()])
    lastname = f.StringField('lastname', validators=[InputRequired()])
    password = f.PasswordField('password', validators=[InputRequired()])
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']
  

class UnregisterForm(FlaskForm):
    password = f.PasswordField('password', validators=[InputRequired()])
    display = ['password']


class SendForm(FlaskForm):
    message = f.StringField('Message', widget=TextArea(), validators=[InputRequired(), Length(max=1024)])
    # more than one user is supported, insert multiple mail addresses separated by a comma
    recipient = f.StringField('Recipient', validators=[InputRequired()])
    time = DateTimeLocalField('Send on', format='%Y-%m-%dT%H:%M', validators=[InputRequired(), time_validator(startdate=datetime.now())])
    is_draft = BooleanField('Is draft')
    display = ['message', 'time', 'recipient', 'is_draft']

class RecipientsListForm(FlaskForm):
    # choices must be declared empty because it has dynamic content, initialized at its instantiation
    radio_form = f.RadioField('Select a recipient:', choices=[])
