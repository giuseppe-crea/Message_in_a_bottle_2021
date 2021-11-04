import unittest
from monolith.classes.tests import utils
from monolith.database import User, Message, db


# noinspection DuplicatedCode
class TestContentFilter(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        """
        Initialize the testing app for all the tests of the class.
        """
        super(TestContentFilter, self).__init__(*args, **kwargs)
        self.app = utils.get_testing_app()

    def test_get_empty(self):
        """
            Test the content filter for a new user.
        """
        with self.app:
            # create a new user
            email, password = utils.create_ex_usr(self.app)
            # the new user logs in
            utils.login(self.app, email, password)
            # get content_filter.html page
            rv = self.app.get('/content_filter')
            # by default the content filter is disabled
            assert rv.status_code == 200
            self.assertIn(b'disabled', rv.data)

            # check DB state
            self.assertEqual(db.session.query(User).
                             filter(User.email == email).
                             first().content_filter, False)

    def test_activation(self):
        """
            Test content filter activation
        """
        with self.app:
            # create a new user
            email, password = utils.create_ex_usr(self.app)
            # the new user logs in
            utils.login(self.app, email, password)
            # get content_filter.html page
            rv = self.app.get('/content_filter')
            # by default the content filter is disabled
            assert rv.status_code == 200
            self.assertIn(b'disabled', rv.data)

            # checkbox click
            rv = self.app.post(
                '/content_filter',
                data={'content_filter': 'on'},
                follow_redirects=True
            )
            # redirected to /content_filter
            assert rv.status_code == 200
            assert b'enabled' in rv.data

            # check DB state
            self.assertEqual(db.session.query(User).
                             filter(User.email == email).
                             first().content_filter, True)

    def test_contentfilter(self):
        """
            Test content filter functionality
        """
        with self.app:
            # create a new user
            email, password = utils.create_ex_usr(self.app)
            # the new user logs in
            utils.login(self.app, email, password)
            # get content_filter.html page
            rv = self.app.get('/content_filter')
            # by default the content filter is disabled
            assert rv.status_code == 200
            self.assertIn(b'disabled', rv.data)

            # checkbox click
            rv = self.app.post(
                '/content_filter',
                data={'content_filter': 'on'},
                follow_redirects=True
            )
            # redirected to /content_filter
            assert rv.status_code == 200
            assert b'enabled' in rv.data

            # check DB state
            self.assertEqual(db.session.query(User).
                             filter(User.email == email).
                             first().content_filter, True)

            # create a second user
            email2, password2 = utils.create_ex_usr(self.app)
            # the second user logs in
            utils.login(self.app, email2, password2)

            # try POST-ing a message to a single user
            rv = self.app.post(
                '/send',
                data={
                    'message': "fuck you",
                    'recipient': email,
                    'time': "2199-01-01T01:01"},
                follow_redirects=True
            )
            assert rv.status_code == 200

            # the returned page
            self.assertIn(b'Message "fuck you" was:', rv.data)
            self.assertIn(b'Successfully Sent to:', rv.data)

            # the message actually is not sent
            self.assertEqual(db.session.query(Message).
                             filter(Message.sender_email == email,
                                    Message.receiver_email == email2,
                                    Message.message == "fuck you").first(),
                             None)
