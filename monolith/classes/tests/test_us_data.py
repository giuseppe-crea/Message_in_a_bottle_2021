import unittest
from monolith.classes.tests.utils import get_testing_app


class TestUsData(unittest.TestCase):
    """
    Tests for the account's data access feature.
    """

    def test_unauthorized(self):
        """
        Test the case where an unauthorized user attempts to access account data.
        """
        tested_app = get_testing_app()
        response = tested_app.get('/user_data')
        self.assertIn(b'Unauthorized', response.data)  # expected an unauthorized access error page

    def test_authorized(self):
        """
        Test the case where a logged user attempts to access account data.
        """
        tested_app = get_testing_app()
        # the user logs
        login_reply = tested_app.post(
            '/login',
            data={'email': 'example@example.com', 'password': 'admin'},
            follow_redirects=True,
        )
        self.assertEqual(200, login_reply.status_code)  # expected a correct login
        # the user tries to access his data
        response = tested_app.get('/user_data')
        tested_app.get('/logout')  # the user logout to not influence other tests
        # expected a correct access with the correct data displayed
        self.assertIn(b'Your account information:', response.data)
        self.assertIn(b'example@example.com', response.data)
        self.assertIn(b'Admin', response.data)
        self.assertIn(b'2020-10-05', response.data)
