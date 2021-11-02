import unittest
from monolith.classes.tests.utils import get_testing_app, login, create_user


class TestAuth(unittest.TestCase):

    def test_get_login(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/login')
            assert rv.status_code == 200
            assert b'email' in rv.data

    def test_post_login(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Admin",
                "01/01/1990",
                "admin")
            assert rv.status_code == 200
            response = login(tested_app, 'example@example.com', 'admin')
            assert response.status_code == 200

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
            response = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Admin",
                "01/01/1990",
                "admin")
            assert response.status_code == 200
            response = login(tested_app, 'example@example.com', 'admin')
            assert response.status_code == 200
            response = tested_app.get("/logout", follow_redirects=True)
            # the user tries to access his data but he's logged out
            response = tested_app.get('/user_data')
            assert response.status_code == 401
