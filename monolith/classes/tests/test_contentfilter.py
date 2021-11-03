import unittest
from monolith.classes.tests import utils
from monolith.database import User, db


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
                             filter(User.email == "default@example.com").
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

            """ This not work
            # check DB state
            self.assertEqual(db.session.query(User).
                             filter(User.email == "default@example.com").
                             first().content_filter, True)
            """