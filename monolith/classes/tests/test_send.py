import unittest

import flask

from monolith.background import deliver_message, send_unsent_past_due
from monolith.classes.tests.utils import get_testing_app, login, create_user, \
    create_message, create_ex_users


class TestSend(unittest.TestCase):
    def test_send_message(self):
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
            # try POST-ing a message to a single user
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert rv.status_code == 200
            self.assertIn(b'Message "Short test message" was:', rv.data)
            self.assertIn(b'Successfully sent to:', rv.data)
            self.assertIn(b'receiver@example.com', rv.data)
            # adding a user,
            # trying to send the same message again to multiple users
            rv = create_user(
                tested_app,
                "otherguy@example.com",
                "Charlie",
                "Charlie",
                "01/01/1990",
                "charlie")
            assert rv.status_code == 200
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com,"
                                 " otherguy@example.com, "
                                 "nonexisting@example.com",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert rv.status_code == 200
            self.assertIn(b'Message "Short test message" was:', rv.data)
            self.assertIn(b'Successfully sent to:', rv.data)
            self.assertIn(b'receiver@example.com', rv.data)
            self.assertIn(b'otherguy@example.com', rv.data)
            self.assertIn(b'Failed to send to:', rv.data)
            self.assertIn(b'nonexisting@example.com', rv.data)
            # now test a message with an invalid send date
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "receiver@example.com",
                    'time': "1999-01-01T01:01"},
                follow_redirects=True
            )
            self.assertIn(b"delivery date earlier than", rv.data)
            # try sending a message to ourselves
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "sender@example.com",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            self.assertIn(b'Failed to send to:', rv.data)
            self.assertIn(b'sender@example.com', rv.data)
            # trying to send empty fields
            rv = tested_app.post(
                '/send',
                data={
                    'message': "",
                    'recipient': "sender@example.com",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert b'This field is required.' in rv.data
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert b'This field is required.' in rv.data
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "sender@example.com",
                    'time': ""},
                follow_redirects=True
            )
            assert b'This field is required.' in rv.data
            # trying to send only invalid mails
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "sender@example.",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert b'You must specify at least one valid address!' in rv.data
            # try to logout and access send
            tested_app.get('/logout')
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "sender@example.com",
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert rv.status_code == 401
            rv = tested_app.get('send')
            assert rv.status_code == 401

    """
    def test_check_mail(self):
        assert check('valid@mail.com') is True
        assert check('invalid@mail.c') is False
        assert check('aghap39') is False
        assert check(' arish .com') is False
        assert check('almost @ real.com') is False"""

    def test_periodic_send(self):
        tested_app = get_testing_app()
        with tested_app:
            users = create_ex_users(tested_app, 2)
            user1, pass1 = users[0]
            user2, pass2 = users[1]
            create_message(
                "old message not yet sent by mistake",
                user1,
                user2,
                "2000-01-01T01:01",
                None,
                1
            )
            # check that the message isn't in user2's inbox
            rv = login(tested_app, user2, pass2)
            assert rv.status_code == 200
            rv = tested_app.get('/inbox')
            assert rv.status_code == 200
            assert bytes(user1, 'utf-8') not in rv.data
            # call the periodic send method
            send_unsent_past_due(flask.current_app)
            # check that the message is now there
            rv = tested_app.get('/inbox')
            assert rv.status_code == 200
            assert bytes(user1, 'utf-8') in rv.data

    def test_send_non_existing_message(self):
        tested_app = get_testing_app()
        with tested_app:
            create_ex_users(tested_app, 1)
            deliver_message(flask.current_app, 1)
            # nothing to assert as a result but all exceptions were handled
            pass
