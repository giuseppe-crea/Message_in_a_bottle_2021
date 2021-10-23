import unittest
from monolith.classes.tests.utils import get_testing_app


def login(client, username, password):
    return client.post(
                '/login',
                data={'email': username, 'password': password},
                follow_redirects=True
            )


class TestHome(unittest.TestCase):
    def test_get_login(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/login')
            assert rv.status_code == 200
            assert b'email' in rv.data

    def test_post_login(self):
        tested_app = get_testing_app()
        with tested_app:
            login_reply = tested_app.get("/login")
            self.assertEqual(login_reply.status_code, 200)
            response = login(tested_app, 'example@example.com', 'admin')
            self.assertIn(b'Hi Admin', response.data)

    def test_bad_login(self):
        tested_app = get_testing_app()
        with tested_app:
            login_reply = login(tested_app, 'bad@wrong.com', 'badpassword')
            self.assertEqual(login_reply.status_code, 401)

    def test_empty_forms_login(self):
        tested_app = get_testing_app()
        with tested_app:
            login_reply = login(tested_app, '', 'badpassword')
            assert b'This field is required.' in login_reply.data
            login_reply = login(tested_app, 'baduser@mail.com', '')
            assert b'This field is required.' in login_reply.data

    def test_login_logout(self):
        tested_app = get_testing_app()
        with tested_app:
            response = login(tested_app, 'example@example.com', 'admin')
            self.assertIn(b'Hi Admin', response.data)
            response = tested_app.get("/logout", follow_redirects=True)
            assert b'Hi Anonymous' in response.data


