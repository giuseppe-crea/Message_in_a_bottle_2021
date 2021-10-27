import unittest
from monolith.classes.tests.utils import get_testing_app, login, create_user


class TestHome(unittest.TestCase):
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
            self.assertIn(b'Hi Alice', response.data)
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
            self.assertIn(b'Successfully Sent to:', rv.data)
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
            self.assertIn(b'Successfully Sent to:', rv.data)
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
