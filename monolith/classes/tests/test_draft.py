import unittest
from monolith.classes.tests.utils import get_testing_app, login, create_user


class TestHome(unittest.TestCase):

    def test_draft_page_view(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/send_draft_list')
            assert rv.status_code == 401
            login(tested_app, 'default@example.com', 'admin')
            rv = tested_app.get('/send_draft_list')
            assert rv.status_code == 200
            assert b'Home' in rv.data

    def test_saving_loading(self):
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
            login(tested_app, 'default@example.com', 'admin')
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "example@example.com",
                    'time': "2199-01-01T01:01",
                    'save_button': True,
                    'file': None
                },
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Hi Admin' in rv.data
            # get the list, we expect to see a mail addressed to example
            rv = tested_app.get('/send_draft_list')
            assert rv.status_code == 200
            assert b'example@example.com' in rv.data
            # get that message
            rv = tested_app.get('/send/1', follow_redirects=True)
            assert rv.status_code == 200
            assert b'Short test message' in rv.data
            # get a message which doesn't exist
            rv = tested_app.get('/send/2', follow_redirects=True)
            assert rv.status_code == 404

    def test_anonymous_access(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/send_draft_list', follow_redirects=True)
            assert rv.status_code == 401
            rv = tested_app.get('/send/1', follow_redirects=True)
            assert rv.status_code == 401
