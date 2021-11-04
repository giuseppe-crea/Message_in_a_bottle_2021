import datetime
import os
from monolith import app
from monolith.auth import login_manager
from monolith.database import db, User, Message


def get_testing_app():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../T_mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOADED_IMAGES_DEST'] = './monolith/static/images/uploads/'
    # clean old db
    if os.path.exists('./T_mmiab.db'):
        os.remove('./T_mmiab.db')
    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)
    with app.app_context():
        example = User()
        example.firstname = 'Admin'
        example.lastname = 'Admin'
        example.email = 'default@example.com'
        example.date_of_birth = datetime.datetime(2020, 10, 5)
        example.is_admin = True
        example.set_password('admin')
        db.session.add(example)
        db.session.commit()
    return app.test_client()


# utility function to log in a user in the tests
# through a post request to /login
def login(client, username, password):
    return client.post(
        '/login',
        data={'email': username, 'password': password},
        follow_redirects=True
    )


# utility function to create a new user in the tests
# through a post request to /create_user
def create_user(client, mail, firstname, lastname, date_of_birth, password):
    return client.post(
        '/create_user',
        data={'email': mail,
              'firstname': firstname,
              'lastname': lastname,
              'date_of_birth': date_of_birth,
              'password': password},
        follow_redirects=True
    )


# a counter to create uniques example users
next_example_user = 1


def create_ex_usr(client):
    """
    Create an unique example user with username = user<counter and
    this data:
    (username@example.com, username, username, "02/02/2000", passusername)
    :param client: the testing app
    :return: (email, password) of the new user
    """
    global next_example_user
    name = "user" + str(next_example_user)
    next_example_user += 1
    email = name + "@example.com"
    password = "pass" + name
    create_user(client, email, name, name, "02/02/2000", password)
    return email, password


def create_ex_users(client, number):
    """
    Create multiple example users
    :param client: the testing app
    :param number: number of users to create
    :return: list of (email, password) tuple of the new users
    """
    return [create_ex_usr(client) for _ in range(number)]


def create_message(message, sender, receiver, time, image, status):
    unsent_message = Message()
    unsent_message.add_message(
        message,
        sender,
        receiver,
        time,
        image,
        status
    )
    db.session.add(unsent_message)
    db.session.commit()
    return unsent_message
