from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=0)
    content_filter = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

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

    def add_points(self, points):
        self.points = self.points + points

    def set_points(self, points):
        self.points = points

    def get_points(self):
        return self.points

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'password':
                self.set_password(value)
            # prevent privilege de/escalation
            elif key != 'is_admin' or key != 'is_anonymous' or key != 'points':
                setattr(self, key, value)

    def get_content_filter_status(self):
        return self.content_filter


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
    # two columns: visible to sender, visible to receiver, for deletion
    # when both are set to false, the message is deleted
    visible_to_sender = db.Column(db.Boolean, nullable=False)
    visible_to_receiver = db.Column(db.Boolean, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def add_message(self, message, sender_email, receiver_email, time, image,
                    status, visible_to_receiver=True):
        """
        adds a message to database, initializing to empty all missing fields
        """
        if message is not None:
            self.message = message
        else:
            self.message = ''
        self.sender_email = sender_email
        if receiver_email is not None:
            self.receiver_email = receiver_email
        else:
            self.receiver_email = ''
        if time is not None:
            self.time = time
        else:
            self.time = ''
        if image is not None:
            self.image = image
        else:
            self.image = ''
        self.status = status
        self.visible_to_sender = True
        if not visible_to_receiver:
            self.visible_to_receiver = False
        else:
            self.visible_to_receiver = True
        self.is_read = False

    def get_id(self):
        """
        :return: message id for this object
        """
        return self.id

    def get_status(self):
        """
        :return: message status for this object
        """
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


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_email = db.Column(db.Unicode(128), nullable=False)
    reported_email = db.Column(db.Unicode(128), nullable=False)
    description = db.Column(db.Unicode(1024), nullable=False)
    timestamp = db.Column(db.Unicode(128), nullable=False)

    def __init__(self, *args, **kw):
        super(Report, self).__init__(*args, **kw)

    def add_report(self, author_email, reported_email, description, timestamp):
        self.author_email = author_email
        self.reported_email = reported_email
        self.description = description
        self.timestamp = timestamp

    def get_id(self):
        return self.id


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.Unicode(128), nullable=False)
    title = db.Column(db.Unicode(256), nullable=False)
    description = db.Column(db.Unicode(1024), nullable=False)
    timestamp = db.Column(db.Unicode(128), nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Notification, self).__init__(*args, **kw)

    def add_notification(self, user_email, title, description,
                         timestamp, is_read):
        self.user_email = user_email
        self.title = title
        self.description = description
        self.timestamp = timestamp
        self.is_read = is_read

    def get_id(self):
        return self.id
