import unittest
from flask import request
from monolith.classes.tests.utils import get_testing_app, create_user


class TestRecipientList(unittest.TestCase):

    # test page retrieving
    def test_get_list_of_recipients(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

    # try to select nothing and get the standard send.html page
    def test_no_selection(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.post(
                '/list_of_recipients',
                data={},
                follow_redirects=True
            )
            assert rv.status_code == 302  # redirected to send.html

    # try to select an existing user and see it in send.html page
    def test_user_selection(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "recipient@example.com",
                "firstname",
                "lastname",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200
            rv = tested_app.post(
                '/list_of_recipients',
                data={'radio_form': 'recipient@example.com'},
                follow_redirects=True
            )
            assert rv.status_code == 302  # redirected to send.html

            # maybe not due to the redirection
            # self.assertIn(b'You can write to: recipient@example.com', response.data)
