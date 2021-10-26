import unittest
from monolith.classes.tests.utils import create_user, get_testing_app, login


class TestUnreg(unittest.TestCase):
    # a non-authenticated user cannot delete his account
    def test_unauthorized(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/unregister')
            assert rv.status_code == 401

    # an authenticated user can delete his account
    def test_authorized(self):
        tested_app = get_testing_app()
        # the user registers
        with tested_app:
            rv = create_user(
                tested_app,
                "user@example.com",
                "name",
                "surname",
                "01/01/1990",
                "password")
            assert rv.status_code == 200

            # the user logs in
            response = login(tested_app, 'user@example.com', 'password')
            assert response.status_code == 200

            # get the unregister page
            rv = tested_app.get('/unregister')
            assert rv.status_code == 200

            # the user tries to delete his account with a wrong password
            rv = tested_app.post(
                '/unregister',
                data={'password': "wrong_pass"},
                follow_redirects=True
            )
            assert rv.status_code == 401

            # the user tries to delete his account with the correct password
            rv = tested_app.post(
                '/unregister',
                data={'password': "password"},
                follow_redirects=True
            )
            assert rv.status_code == 200

            # the user tries to login but his account does no longer exist
            response = login(tested_app, 'user@example.com', 'password')
            assert response.status_code == 401



