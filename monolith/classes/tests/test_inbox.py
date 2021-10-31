import datetime
import unittest

import flask

from monolith.background import deliver_message
from monolith.classes.tests import utils
from monolith.classes.tests.utils import get_testing_app, create_user, login


class TestHome(unittest.TestCase):
    # test the presence of a message in the outbox of the sender
    # and inbox of the receiver
    def test_read_message(self):
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
            assert b'Alice Alice' in rv.data
            # login as Alice
            rv = login(tested_app, 'sender@example.com', 'alice')
            assert rv.status_code == 200
            assert b'Hi Alice' in rv.data
            # send a message to default@example.com with no wait
            # this doesn't actually use celery
            delivery_time = datetime.datetime.now()
            deliver_message(
                flask.current_app,
                "Test1",
                "sender@example.com",
                "default@example.com",
                delivery_time.strftime('%Y-%m-%dT%H:%M')
            )
            # check the outbox
            rv = tested_app.get('/outbox', follow_redirects=True)
            assert rv.status_code == 200
            assert b'default@example.com' in rv.data
            # check that specific message
            rv = tested_app.get('/outbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Test1' in rv.data
            # let's log out and see if we can find it on default@example.com
            rv = tested_app.get('/logout', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Hi Anonymous' in rv.data
            rv = login(tested_app, 'default@example.com', 'admin')
            assert rv.status_code == 200
            assert b'Hi Admin' in rv.data
            rv = tested_app.get('/inbox', follow_redirects=True)
            assert rv.status_code == 200
            assert b'sender@example.com' in rv.data
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Test1' in rv.data
            # logout, make sure nobody else can see this message
            rv = tested_app.get('/logout', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Hi Anonymous' in rv.data
            # check both outbox and inbox as anonymous user
            rv = tested_app.get('/outbox', follow_redirects=True)
            assert rv.status_code == 401
            rv = tested_app.get('/outbox/1', follow_redirects=True)
            assert rv.status_code == 401
            rv = tested_app.get('/inbox', follow_redirects=True)
            assert rv.status_code == 401
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            assert rv.status_code == 401
            # log in with a user that did NOT receive the message
            # then try to access the message by id
            rv = create_user(
                tested_app,
                "intruder@example.com",
                "Eve",
                "Nosy",
                "01/01/1990",
                "eve")
            assert rv.status_code == 200
            assert b'Eve Nosy' in rv.data
            rv = login(tested_app, 'intruder@example.com', 'eve')
            assert rv.status_code == 200
            assert b'Hi Eve' in rv.data
            rv = tested_app.get('/outbox', follow_redirects=True)
            assert rv.status_code == 200
            rv = tested_app.get('/outbox/1', follow_redirects=True)
            assert rv.status_code == 403
            rv = tested_app.get('/inbox', follow_redirects=True)
            assert rv.status_code == 200
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            assert rv.status_code == 403

    def test_forward(self):
        """
        Test the message forward functionality.
        """
        tested_app = get_testing_app()
        with tested_app:
            # create 2 users
            users = utils.create_ex_users(tested_app, 2)
            user1, password1 = users[0]
            user2, password2 = users[1]
            # internally send a message to user2 from user1
            delivery_time = datetime.datetime.now()
            deliver_message(
                flask.current_app,
                "Test1",
                user1,
                user2,
                delivery_time.strftime('%Y-%m-%dT%H:%M')
            )

            # log as user2
            utils.login(tested_app, user2, password2)
            # the message is present
            rv = tested_app.get('/inbox')
            self.assertIn(bytes(user1, 'utf-8'), rv.data)
            rv = tested_app.get('/inbox/1')
            self.assertEqual(rv.status_code, 200)

            # forward the message
            time = "2199-01-01T01:01"
            rv = tested_app.post(
                '/inbox/forward/1',
                data={
                    'recipient': user1,
                    'time': time},
                follow_redirects=True
            )
            # the message is correctly sent
            self.assertIn(b'Successfully Sent to:', rv.data)
