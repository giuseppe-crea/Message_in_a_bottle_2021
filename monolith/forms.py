import re
from datetime import datetime

import wtforms as f
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import UploadSet, IMAGES
from wtforms import widgets, SelectMultipleField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import StopValidation, InputRequired, Length, Optional

images = UploadSet('images', IMAGES, default_dest=None)


class TimeValidator(object):
    """
    Custom validator for our datetime field
    it takes care to ignore seconds in its comparison
    and prevents the user from sending messages into the past
    """
    field_flags = ('required',)

    # this validator strips times down to the minute
    # our delivery method will instantly deliver anything with a negative
    # timestamp, making this reliable
    def __init__(self, startdate=datetime.now(), message=None):
        """
        Initializer for the TimeValidator class

        :param startdate: the earliest valid date
        :param message: optional custom error message
        """
        self.startdate = startdate.replace(second=0, microsecond=0)
        if not message:
            message = "You can't set a delivery date earlier than " + \
                      startdate.strftime("%m/%d/%Y, %H:%M") + "!"
        self.message = message

    def __call__(self, form, field):
        if field.data.replace(second=0, microsecond=0) < self.startdate:
            field.errors[:] = []
            raise StopValidation(self.message)


class MailValidator(object):
    """
    custom validator for mails, more powerful than a normal MailField
    It can check a whole list of comma-separated mails
    """
    @staticmethod
    def check(email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # pass the regular expression
        # and the string into the fullmatch() method
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def __init__(self, mails=None, message=None, single=False):
        """
        Initializer for the MailValidator class

        :param mails: string to validate
        :param message: optional custom error message
        :param single: set to true if the mails param must validate to len 1
        """
        if mails is None:
            mails = []
        self.mails = mails
        self.single = single
        if not message:
            message = "You must specify at least one valid address!"
        self.message = message

    def __call__(self, form, field):
        self.mails = []
        to_parse = field.data.split(', ')
        for address in to_parse:
            address = address.strip()
            if self.check(address):
                self.mails.append(address)
        if len(self.mails) > 1 and self.single:
            field.errors[:] = []
            raise StopValidation(self.message)
        if len(self.mails) < 1:
            field.errors[:] = []
            raise StopValidation(self.message)
        elif len(self.mails) == 1:
            field.data = self.mails.pop(0)
        else:
            field.data = ', '.join(self.mails)


time_validator = TimeValidator
mail_validator = MailValidator


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[InputRequired()])
    password = f.PasswordField('password', validators=[InputRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField(
        'email',
        validators=[InputRequired(), mail_validator(message="Invalid email!")])
    firstname = f.StringField('firstname', validators=[InputRequired()])
    lastname = f.StringField('lastname', validators=[InputRequired()])
    password = f.PasswordField('password', validators=[InputRequired()])
    date_of_birth = f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']


class UnregisterForm(FlaskForm):
    password = f.PasswordField('password', validators=[InputRequired()])
    display = ['password']


class SendForm(FlaskForm):
    message = f.StringField(
        'Message',
        validators=[InputRequired(), Length(max=1024)]
    )
    # more than one user is supported,
    # insert multiple mail addresses separated by a comma
    recipient = f.StringField(
        'Recipient',
        validators=[InputRequired(), mail_validator(), Length(max=1024)]
    )
    time = DateTimeLocalField(
        'Send on',
        format='%Y-%m-%dT%H:%M',
        validators=[InputRequired(), time_validator(startdate=datetime.now())]
    )
    file = FileField(
        'Your picture (optional)',
        validators=[FileAllowed(images, 'Images only!')]
    )
    display = ['message', 'time', 'recipient', 'file']


class ReplyForm(FlaskForm):
    message = f.StringField(
        'Message',
        validators=[InputRequired(), Length(max=1024)]
    )
    time = DateTimeLocalField(
        'Send on',
        format='%Y-%m-%dT%H:%M',
        validators=[InputRequired(), time_validator(startdate=datetime.now())]
    )
    display = ['message', 'time']


class ForwardForm(FlaskForm):
    # more than one user is supported,
    # insert multiple mail addresses separated by a comma
    recipient = f.StringField(
        'Recipient',
        validators=[InputRequired(), mail_validator()]
    )
    time = DateTimeLocalField(
        'Send on',
        format='%Y-%m-%dT%H:%M',
        validators=[InputRequired(), time_validator(startdate=datetime.now())]
    )
    display = ['time', 'recipient']


# custom class to display checkboxes in the form, based on SelectMultipleField
# to select multiple recipients
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# uses a custom class to render checkboxes
class RecipientsListForm(FlaskForm):
    # choices must be declared empty because it has dynamic content,
    # initialized after its instantiation
    multiple_field_form = MultiCheckboxField('Select recipients:', choices=[])


class EmailForm(FlaskForm):
    """
    Requests an email to the user
    """
    email = f.StringField('email', validators=[InputRequired(),
                                               MailValidator()])
    display = ['email']


class ReportForm(FlaskForm):
    user = f.StringField('User', validators=[InputRequired()])
    description = f.StringField(
        'Description',
        validators=[InputRequired(), Length(max=1024)]
    )
    block_user = f.RadioField(
        'Blacklist User',
        choices=[('yes', 'YES'), ('no', 'NO')],
        default='yes',
        validators=[InputRequired()]
        )

    display = ['user', 'description', 'block_user']


class CredentialsForm(FlaskForm):
    email = f.StringField(
        'email',
        validators=[
            Optional(),
            mail_validator(single=True, message="Not a valid address."),
            Length(max=128)
        ]
    )
    firstname = f.StringField('firstname', validators=[Length(max=128)])
    lastname = f.StringField('lastname', validators=[Length(max=128)])
    old_password = f.PasswordField(
        'old password',
        validators=[InputRequired(), Length(max=128)])
    password = f.PasswordField('new password', validators=[Length(max=128)])
    display = ['email', 'firstname', 'lastname', 'password', 'old_password']


class ContentFilterForm(FlaskForm):
    content_filter_status = f.BooleanField()
