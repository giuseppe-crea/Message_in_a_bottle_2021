import unittest

from monolith.classes.tests.utils import login, get_testing_app, create_user


class TestHome(unittest.TestCase):

    def test_admin_has_access(self):
        tested_app = get_testing_app()
        with tested_app:
            # admin can access the page
            rv = login(tested_app, 'example@example.com', 'admin')
            assert rv.status_code == 200
            rv = tested_app.get('/admin')
            assert rv.status_code == 200

    def test_anonymous_denied(self):
        # anonymous users can't access the page
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/logout', follow_redirects=True)
            assert rv.status_code == 200
            rv = tested_app.get('/admin')
            assert rv.status_code == 401

    def test_non_admin_denied(self):
        # non-admin users can't access the page
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "otherguy@example.com",
                "Charlie",
                "Charlie",
                "01/01/1990",
                "charlie")
            assert rv.status_code == 200
            rv = login(tested_app, 'otherguy@example.com', 'charlie')
            assert rv.status_code == 200
            rv = tested_app.get('/admin')
            assert rv.status_code == 401
