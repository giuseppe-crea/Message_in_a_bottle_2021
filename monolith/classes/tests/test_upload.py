import filecmp
import os
import unittest
from pathlib import Path

import flask

from monolith.background import deliver_message
from monolith.classes.tests.utils import get_testing_app, login, create_user


class TestSend(unittest.TestCase):
    def test_send_and_view_image(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "sender@example.com",
                "Alice",
                "Alice",
                "01/01/1990",
                "alice")
            assert rv.status_code == 200
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "Bob",
                "Bob",
                "01/01/1990",
                "bob")
            assert rv.status_code == 200
            response = login(tested_app, 'sender@example.com', 'alice')
            assert response.status_code == 200
            # completed the registration and login procedures
            # get the send message page
            rv = tested_app.get('/send')
            assert rv.status_code == 200
            # declare loc of Lenna.png
            lenna_src = './monolith/static/images/Lenna.png'
            # declare expected loc of received Lenna.png
            lenna_dst = \
                './monolith/static/images/test_uploads/' \
                'sender-example-com/Lenna.png'
            # assert existence of one, non existence of the other
            assert os.path.isfile(lenna_src)
            assert not os.path.isfile(lenna_dst)
            # try POST-ing a message to a single user
            lenna = open(lenna_src, 'rb')
            file = (lenna, "Lenna.png")
            assert file is not None
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert rv.status_code == 200
            # since we know this is the one and only message its id is #1
            # let's trick celery into sending it
            deliver_message(flask.current_app, 1)
            # logout and check if it has been delivered
            tested_app.get('/logout')
            rv = login(tested_app, 'receiver@example.com', 'bob')
            assert rv.status_code == 200
            # get the message
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Short test message' in rv.data
            assert filecmp.cmp(lenna_src, lenna_dst)
            # clean up
            os.remove(lenna_dst)
            os.rmdir(Path(lenna_dst).parent)

    def test_send_not_a_picture(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "sender@example.com",
                "Alice",
                "Alice",
                "01/01/1990",
                "alice")
            assert rv.status_code == 200
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "Bob",
                "Bob",
                "01/01/1990",
                "bob")
            assert rv.status_code == 200
            response = login(tested_app, 'sender@example.com', 'alice')
            assert response.status_code == 200
            # completed the registration and login procedures
            # get the send message page
            rv = tested_app.get('/send')
            assert rv.status_code == 200
            # declare loc of non-image file
            bad_src = './monolith/app.py'
            # assert existence of... app.py
            assert os.path.isfile(bad_src)
            # try POST-ing a message to a single user
            bad_file = open(bad_src, 'rb')
            file = (bad_file, "app.py")
            assert file is not None
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert b'Images only!' in rv.data

    def test_send_duplicate_picture(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "sender@example.com",
                "Alice",
                "Alice",
                "01/01/1990",
                "alice")
            assert rv.status_code == 200
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "Bob",
                "Bob",
                "01/01/1990",
                "bob")
            assert rv.status_code == 200
            response = login(tested_app, 'sender@example.com', 'alice')
            assert response.status_code == 200
            # completed the registration and login procedures
            # get the send message page
            rv = tested_app.get('/send')
            assert rv.status_code == 200
            # declare loc of Lenna.png
            lenna_src = './monolith/static/images/Lenna.png'
            # declare expected loc of received Lenna.png
            lenna_dst = \
                './monolith/static/images/test_uploads/' \
                'sender-example-com/Lenna.png'
            # assert existence of one, non existence of the other
            assert os.path.isfile(lenna_src)
            assert not os.path.isfile(lenna_dst)
            # try POST-ing a message to a single user
            lenna = open(lenna_src, 'rb')
            file = (lenna, "Lenna.png")
            assert file is not None
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert rv.status_code == 200
            # assert existence of sent picture
            assert os.path.isfile(lenna_dst)
            # let's try sending the same message twice now
            lenna = open(lenna_src, 'rb')
            file = (lenna, "Lenna.png")
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Duplicate filename.' in rv.data
            # clean up
            os.remove(lenna_dst)
            os.rmdir(Path(lenna_dst).parent)

    def test_send_filename_too_long(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "sender@example.com",
                "Alice",
                "Alice",
                "01/01/1990",
                "alice")
            assert rv.status_code == 200
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "Bob",
                "Bob",
                "01/01/1990",
                "bob")
            assert rv.status_code == 200
            response = login(tested_app, 'sender@example.com', 'alice')
            assert response.status_code == 200
            # completed the registration and login procedures
            # get the send message page
            rv = tested_app.get('/send')
            assert rv.status_code == 200
            # declare loc of Lenna.png
            lenna_src = './monolith/static/images/Lenna.png'
            # declare expected loc of received Lenna.png
            lenna_dst = \
                './monolith/static/images/uploads/sender-example-com/Lenna.png'
            # assert existence of one, non existence of the other
            assert os.path.isfile(lenna_src)
            assert not os.path.isfile(lenna_dst)
            # try POST-ing a message to a single user
            lenna = open(lenna_src, 'rb')
            long_string = "a"
            for i in range(1025):
                long_string += "a"
            long_string += ".png"
            file = (lenna, long_string)
            assert file is not None
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Filename too long.' in rv.data
