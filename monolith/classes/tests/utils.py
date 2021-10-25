import os
from datetime import datetime

from monolith import app
from monolith.auth import login_manager
from monolith.database import db, User


def get_testing_app():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../T_mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # clean old db
    if os.path.exists('./T_mmiab.db'):
        os.remove('./T_mmiab.db')
    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)
    return app.test_client()


def login(client, username, password):
    return client.post(
                '/login',
                data={'email': username, 'password': password},
                follow_redirects=True
            )


def create_user(client, mail, firstname, lastname, dateofbirth, password):
    return client.post(
        '/create_user',
        data={'email': mail,
              'firstname': firstname,
              'lastname': lastname,
              'dateofbirth': dateofbirth,
              'password': password},
        follow_redirects=True
    )


# utils.py