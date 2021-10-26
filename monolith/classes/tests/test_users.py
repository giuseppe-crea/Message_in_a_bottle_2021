import unittest
import datetime

from monolith.classes.tests.utils import get_testing_app, login, create_user


class TestHome(unittest.TestCase):
    def test_create_user(self):
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
            rv = tested_app.get('/users')
            assert rv.status_code == 200
            assert b'User List' in rv.data
            assert b'Admin Admin' in rv.data

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
        assert rv.status_code == 400
