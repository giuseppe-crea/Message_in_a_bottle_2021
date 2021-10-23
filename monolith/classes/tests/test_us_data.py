import unittest
from monolith import app
from monolith.classes.tests.utils import get_testing_app


class testUsData(unittest.TestCase):
    def test_unauthorized(self):
        tested_app = get_testing_app()
        response = tested_app.get('/user_data')
        self.assertIn(b'Unauthorized', response.data)

    def test_authorized(self):
        tested_app = get_testing_app()

        login_reply = tested_app.post(
            '/login',
            data={'email':'example@example.com','password':'admin'},
            follow_redirects=True,
        )
        self.assertEqual(200, login_reply.status_code)

        response = tested_app.get('/user_data')
        tested_app.get('/logout')
        self.assertIn(b'Your account information:', response.data)
        self.assertIn(b'example@example.com', response.data)
