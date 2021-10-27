from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

class Draft(db.Model):

    __tablename__ = 'draft'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_email = db.Column(db.Unicode(128), nullable=True)
    recipients = db.Column(db.Unicode(128), nullable=True)
    message = db.Column(db.Unicode(1024), nullable=True)
    # delivery_date = db.Column(db.DateTime, nullable=True)

    def __init__(self, *args, **kw):
        super(Draft, self).__init__(*args, **kw)

    def add_new_draft(self, sender_email, recipients, message, delivery_date):
        self.sender_email = sender_email
        self.recipients = recipients
        self.message = message
        # self.delivery_date = delivery_date

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def register_new_user(self, email, first_name, last_name, password, date_of_birth):
        self.firstname = first_name
        self.lastname = last_name
        self.email = email
        self.set_password(password)
        self.date_of_birth = date_of_birth

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id
