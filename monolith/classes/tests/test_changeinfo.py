import unittest

from monolith.classes.tests.utils import get_testing_app, create_ex_usr, login


class TestSend(unittest.TestCase):
    def test_load_edit_page(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/credentials')
            assert rv.status_code == 401
            user1, password1 = create_ex_usr(tested_app)
            rv = login(tested_app, user1, password1)
            assert rv.status_code == 200
            rv = tested_app.get('/credentials')
            assert rv.status_code == 200
            assert b'change your credentials' in rv.data

    def test_correct_edit(self):
        tested_app = get_testing_app()
        with tested_app:
            user1, password1 = create_ex_usr(tested_app)
            rv = login(tested_app, user1, password1)
            assert rv.status_code == 200
            # post a first name change
            rv = tested_app.post(
                '/credentials',
                data={'firstname': 'NewName', 'old_password': password1},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'NewName' in rv.data
            # now a last name change
            rv = tested_app.post(
                '/credentials',
                data={'lastname': 'Changed', 'old_password': password1},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Changed' in rv.data
            # now a password change
            rv = tested_app.post(
                '/credentials',
                data={'password': 'newpass', 'old_password': password1},
                follow_redirects=True
            )
            # email change
            rv = tested_app.post(
                '/credentials',
                data={'email': 'new@mail.com', 'old_password': 'newpass'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            rv = tested_app.get('/logout', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Login' in rv.data
            # try to login with the new credentials
            rv = login(tested_app, 'new@mail.com', 'newpass')
            assert rv.status_code == 200

    def test_bad_edits(self):
        tested_app = get_testing_app()
        with tested_app:
            user, password = create_ex_usr(tested_app)
            rv = login(tested_app, user, password)
            assert rv.status_code == 200
            # bad email format
            rv = tested_app.post(
                '/credentials',
                data={'email': 's', 'old_password': password},
                follow_redirects=True
            )
            assert b'Not a valid address.' in rv.data
            # wrong password test
            rv = tested_app.post(
                '/credentials',
                data={'email': 'valid@mail.com', 'old_password': 'bad_passw'},
                follow_redirects=True
            )
            assert b'Wrong Password!' in rv.data
