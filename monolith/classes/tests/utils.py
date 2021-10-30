import datetime
import os
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
