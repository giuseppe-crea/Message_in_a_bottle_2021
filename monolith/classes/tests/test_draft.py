import unittest
from monolith.classes.tests.utils import get_testing_app, login, create_ex_usr


class TestHome(unittest.TestCase):

    def test_draft_page_view(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/send_draft_list')
            assert rv.status_code == 401
            login(tested_app, 'example@example.com', 'admin')
            rv = tested_app.get('/send_draft_list')
            assert rv.status_code == 200
            assert b'Your drafts:' in rv.data

    def test_saving_loading(self):
        tested_app = get_testing_app()
        with tested_app:
            mail, password = create_ex_usr(tested_app)
            login(tested_app, mail, password)
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
            # we are redirected to the frontpage after saving a draft
            assert rv.status_code == 200
            self.assertTrue(bytes("Hi, " + mail.split('@')[0], 'utf-8') in
                            rv.get_data())
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
            # test draft removal
            rv = tested_app.delete('/outbox/1', follow_redirects=True)
            assert rv.status_code == 200
            assert b'example@example.com' not in rv.data

    def test_anonymous_access(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/send_draft_list', follow_redirects=True)
            assert rv.status_code == 401
            rv = tested_app.get('/send/1', follow_redirects=True)
            assert rv.status_code == 401
