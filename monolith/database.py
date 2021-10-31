from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


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

    def register_new_user(self, email, first_name, last_name, password,
                          date_of_birth):
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

    def get_email(self):
        return self.email


class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_email = db.Column(db.Unicode(128), nullable=False)
    receiver_email = db.Column(db.Unicode(1028), nullable=False)
    message = db.Column(db.Unicode(1024), nullable=False)
    # for ease of use with Celery, we import this as string
    time = db.Column(db.Unicode(128), nullable=False)
    image = db.Column(db.Unicode(1024), nullable=False)
    # 0 draft, 1 sent, 2 delivered
    status = db.Column(db.Integer, nullable=False)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def add_message(self, message, sender_email, receiver_email, time, image,
                    status):
        self.message = message
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.time = time
        if image is not None:
            self.image = image
        else:
            self.image = ''
        self.status = status

    def get_id(self):
        return self.id

    def get_status(self):
        return self.status


class Blacklist(db.Model):

    __tablename__ = 'blacklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, nullable=False)
    email = db.Column(db.Unicode(128), nullable=False)

    def __init__(self, *args, **kw):
        super(Blacklist, self).__init__(*args, **kw)

    def add_blocked_user(self, owner, email):
        self.owner = owner
        self.email = email

    def get_id(self):
        return self.owner
