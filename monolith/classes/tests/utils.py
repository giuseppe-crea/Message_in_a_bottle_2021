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
    create_user(
        app.test_client(),
        'default@example.com',
        'Admin',
        'Default',
        '05/10/2020',
        'admin'
    )
    return app.test_client()


def login(client, username, password):
    return client.post(
                '/login',
                data={'email': username, 'password': password},
                follow_redirects=True
            )


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
