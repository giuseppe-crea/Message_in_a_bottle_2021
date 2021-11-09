import os
import shutil

import flask

from monolith.app import create_app
from monolith.background import deliver_message
from monolith.database import db, Message


def get_testing_app():
    """
    Create an app instance for testing.
    """
    # cleanup persistent state for a test from scratch
    cleanup()
    _app = create_app()
    return _app.test_client()


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
_next_example_user = 1


def create_ex_usr(client):
    """
    Create an unique example user with username = user<counter and
    this data:
    (username@example.com, username, username, "02/02/2000", passusername)
    :param client: the testing app
    :return: (email, password) of the new user
    """
    global _next_example_user
    name = "user" + str(_next_example_user)
    _next_example_user += 1
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


def int_send_mess(sender, receiver, text, delivery_time):
    """
    Internally send a message, for testing.
    """
    message = create_message(
        text,
        sender,
        receiver,
        delivery_time.strftime('%Y-%m-%dT%H:%M'),
        None,
        1
    )
    deliver_message(flask.current_app, message.get_id())


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


def cleanup():
    if os.path.exists('./T_mmiab.db'):
        print("Removing old database...")
        os.remove('./T_mmiab.db')
    folder = './monolith/static/images/test_uploads'
    if os.path.isdir(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
