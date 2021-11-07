import unittest
from monolith.classes.tests.utils import get_testing_app, create_user, login


class TestRecipientList(unittest.TestCase):

    # # # # # # # # # # # # test unauthorized access # # # # # # # # # # # #
    def test_unauthorized_access(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 401

    # # # # # # # # # # test several functionalities # # # # # # # # # # #
    def test_listing(self):
        # test page retrieving
        tested_app = get_testing_app()
        with tested_app:
            # create a user which will look for
            # the list of available recipients
            rv = create_user(
                tested_app,
                "tester@example.com",
                "tester",
                "tester",
                "12/12/1999",
                "password"
            )
            assert rv.status_code == 200

            # login with the tester user
            response = login(tested_app, 'tester@example.com', 'password')
            assert response.status_code == 200

            # retrieve list_of_recipients.html
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

            # the page automatically produces a post request
            # to /live_search with void data
            # that results in the entire DB display
            rv = tested_app.post(
                '/live_search',
                data={'query': ''},
                follow_redirects=True
            )
            assert rv.status_code == 200
            # tester address and admin address
            assert b'Choose Recipients' in rv.data
            assert b'example@example.com' in rv.data
            assert b'tester@example.com' not in rv.data

            # try to select an existing user
            # create a possible recipient
            rv = create_user(
                tested_app,
                "recipient@example.com",
                "firstname",
                "lastname",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200

            # keyboard input of 'q'
            # not exists an account with a 'q'
            # in his information
            rv = tested_app.post(
                '/live_search',
                data={'query': 'q'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'q' not in rv.data

            # keyboard input of 'test'
            # exists an account with a 'test'
            # in his information (tester)
            # it won't be displayed because it's the searching account itself
            rv = tested_app.post(
                '/live_search',
                data={'query': 'test'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Choose Recipients' in rv.data
            assert b'tester@example.com' not in rv.data
            assert b'recipient@example.com' not in rv.data
            # same test but with 'r'
            rv = tested_app.post(
                '/live_search',
                data={'query': 'r'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Choose Recipients' in rv.data
            assert b'recipient@example.com' in rv.data

            # void POST request (no recipient selection)
            rv = tested_app.post(
                '/list_of_recipients',
                data={},
                follow_redirects=True
            )
            assert rv.status_code == 200
            # back to /send
            assert b'Message' in rv.data

            # submitting one existing user selection
            # no redirection
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        'recipient@example.com'},
                follow_redirects=False
            )
            assert rv.status_code == 302
            assert rv.location == \
                   "http://localhost/send?data=recipient%40example.com"

            # testing with redirection
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        'recipient@example.com'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Message' in rv.data
            # cannot test the presence of recipient@example.com
            # inserted in JS after the http response

            # create another possible recipient
            rv = create_user(
                tested_app,
                "second_recipient@example.com",
                "firstname",
                "lastname",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200

            # selection of two user and POST request (without redirection)
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        ['first_recipient@example.com',
                         'second_recipient@example.com']},
                follow_redirects=False
            )
            assert rv.status_code == 302
            assert rv.location == \
                   "http://localhost/send?data=first_recipient%40example.com" \
                   "%2C+second_recipient%40example.com"

            # selection of two user and POST request (with redirection)
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        ['first_recipient@example.com',
                         'second_recipient@example.com']},
                follow_redirects=True
            )
            assert rv.status_code == 200
            assert b'Message' in rv.data
