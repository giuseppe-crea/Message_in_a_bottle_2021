import unittest

from monolith.classes.tests.utils import get_testing_app, create_user


class TestHome(unittest.TestCase):
    def test_create_user(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/create_user', follow_redirects=True)
            assert rv.status_code == 200
            assert b'email' in rv.data
            rv = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Amint",
                "01/01/1990",
                "admin")
            assert rv.status_code == 200
            rv = tested_app.get('/users')
            assert rv.status_code == 200
            assert b'User List' in rv.data
            assert b'Admin Amint' in rv.data

    def test_invalid_form_values(self):
        tested_app = get_testing_app()
        with tested_app:
            # invalid mail
            rv = create_user(
                tested_app,
                "example@example.c",
                "Admin",
                "Amint",
                "01/01/1990",
                "admin")
            assert rv.status_code == 200
            assert b'Invalid email!' in rv.data
            rv = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Amint",
                "01/01/19900",
                "admin")
            assert rv.status_code == 200
            assert b'Not a valid date value' in rv.data
            rv = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Amint",
                "01/01/1990",
                "")
            assert rv.status_code == 200
            assert b'This field is required.' in rv.data
            print(rv.data)
            rv = create_user(
                tested_app,
                "example@example.com",
                "",
                "Amint",
                "01/01/1990",
                "admin")
            assert rv.status_code == 200
            assert b'This field is required.' in rv.data
            rv = create_user(
                tested_app,
                "",
                "Admin",
                "Amint",
                "01/01/1990",
                "admin")
            assert rv.status_code == 200
            assert b'This field is required.' in rv.data
            rv = create_user(
                tested_app,
                "example@example.com",
                "Admin",
                "Amint",
                "",
                "admin")
            assert rv.status_code == 200
            assert b'Not a valid date value' in rv.data

    def test_create_duplicate_user(self):
        tested_app = get_testing_app()
        rv = create_user(
            tested_app,
            "example@example.com",
            "Admin",
            "Admin",
            "01/01/1990",
            "admin")
        assert rv.status_code == 200
        rv = create_user(
            tested_app,
            "example@example.com",
            "Admin",
            "Admin",
            "01/01/1990",
            "admin")
        assert rv.status_code == 200
        assert b'already in use' in rv.data
