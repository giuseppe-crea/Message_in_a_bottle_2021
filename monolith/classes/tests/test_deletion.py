import os
import unittest
from pathlib import Path

import flask
from slugify import slugify

from monolith.background import deliver_message, cleanup_pictures
from monolith.database import Message
from monolith.classes.tests.utils import get_testing_app, create_ex_users, \
    login, create_message


class TestSend(unittest.TestCase):
    def test_correct_removal(self):
        tested_app = get_testing_app()
        with tested_app:
            users = create_ex_users(tested_app, 3)
            user1, password1 = users[0]
            user2, password2 = users[1]
            user3, password3 = users[2]
            # this test uses the upload function to showcase how
            # unused pics are removed from the server
            lenna_src = './monolith/static/images/Lenna.png'
            lenna_dst = \
                './monolith/static/images/test_uploads/' + \
                slugify(user1) + \
                '/Lenna.png'
            lenna = open(lenna_src, 'rb')
            file = (lenna, "Lenna.png")
            assert os.path.isfile(lenna_src)
            assert not os.path.isfile(lenna_dst)
            rv = login(tested_app, user1, password1)
            assert rv.status_code == 200
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': user2+', '+user3,
                    'time': "2199-01-01T01:01",
                    'file': file
                },
                content_type='multipart/form-data',
                follow_redirects=True
            )
            assert rv.status_code == 200
            # check that the message has been added to the database
            message = Message().query.filter_by(id=int(1))
            assert message is not None
            # deliver the messages
            deliver_message(flask.current_app, 1)
            deliver_message(flask.current_app, 2)
            # assert that the new pic has been saved
            assert os.path.isfile(lenna_dst)
            # try and view the message in my inbox
            rv = tested_app.get('/outbox', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user2, 'utf-8') in rv.data
            # now delete it for the sender
            rv = tested_app.delete('/outbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user2, 'utf-8') not in rv.data
            # check that the message is still present for user2
            tested_app.get('/logout')
            rv = login(tested_app, user2, password2)
            assert rv.status_code == 200
            rv = tested_app.get('/inbox', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user1, 'utf-8') in rv.data
            # now delete it for the receiver
            rv = tested_app.delete('/inbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user1, 'utf-8') not in rv.data
            # check that the message has been deleted from the database
            message = Message().query.filter_by(id=int(1)).first()
            assert message is None
            # call pic cleanup service
            cleanup_pictures(flask.current_app)
            # check that the received pic hasn't been deleted
            assert os.path.isfile(lenna_dst)
            tested_app.get('/logout')
            # now delete it for user3 too
            rv = login(tested_app, user3, password3)
            assert rv.status_code == 200
            rv = tested_app.delete('/inbox/2', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user1, 'utf-8') not in rv.data
            # check that the message hasn't been deleted from the database
            message = Message().query.filter_by(id=int(2)).first()
            assert message is not None
            # call pic cleanup service
            cleanup_pictures(flask.current_app)
            # check that the received pic hasn't been deleted
            assert os.path.isfile(lenna_dst)
            tested_app.get('/logout')
            # finally, log back as user1, delete message 2
            rv = login(tested_app, user1, password1)
            assert rv.status_code == 200
            rv = tested_app.delete('/outbox/2', follow_redirects=True)
            assert rv.status_code == 200
            assert bytes(user3, 'utf-8') not in rv.data
            # call pic cleanup service
            cleanup_pictures(flask.current_app)
            # check that the received pic hasn't been deleted
            assert not os.path.isfile(lenna_dst)
            # cleanup the empty user folder
            os.rmdir(Path(lenna_dst).parent)

    def test_nonexistent(self):
        tested_app = get_testing_app()
        with tested_app:
            users = create_ex_users(tested_app, 1)
            user1, password1 = users[0]
            login(tested_app, user1, password1)
            rv = tested_app.delete('/outbox/1', follow_redirects=True)
            assert rv.status_code == 403

    def test_delete_unauthorized(self):
        tested_app = get_testing_app()
        with tested_app:
            users = create_ex_users(tested_app, 2)
            user1, password1 = users[0]
            user2, password2 = users[1]
            # login as user1
            login(tested_app, user1, password1)
            # create a delivered message in the database, from user2 to user1
            create_message("test", user2, user1, "2199-01-01T01:01", None, 2)
            # try and delete it from user2's outbox
            rv = tested_app.delete('/outbox/1', follow_redirects=True)
            assert rv.status_code == 403
            tested_app.get('/logout')
            # login as user2
            login(tested_app, user2, password2)
            # try and delete it from user1's inbox
            rv = tested_app.delete('/inbox/1', follow_redirects=True)
            assert rv.status_code == 403
