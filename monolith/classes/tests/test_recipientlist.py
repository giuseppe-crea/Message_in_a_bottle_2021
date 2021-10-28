import unittest
from monolith.classes.tests.utils import get_testing_app, create_user, login


class TestRecipientList(unittest.TestCase):

    # # # # # # # # # # # # # test page retrieving # # # # # # # # # # # # #
    def test_get_list_of_recipients(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

    # # # # # # # # # # # try to select an existing user # # # # # # # # # # #
    def test_user_selection(self):
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

            # login with the tester user
            response = login(tested_app, 'tester@example.com', 'password')
            self.assertIn(b'Hi tester', response.data)

            # retrieve list_of_recipients.html
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

            # selection of a user and POST request
            rv = tested_app.post(
                '/list_of_recipients',
                data={'multiple_field_form': 'recipient@example.com'},
                follow_redirects=True
            )

            assert rv.status_code == 200

    # # # # # # # # # # # test the submitting of a void form # # # # # # # #
    def test_no_selection(self):
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
            self.assertIn(b'Hi tester', response.data)

            # retrieve list_of_recipients.html
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

            # check HTML consistency
            self.assertIn(b'tester tester: tester@example.com', rv.data)

            # void POST request (no recipient selection)
            rv = tested_app.post(
                '/list_of_recipients',
                data={},
                follow_redirects=True
            )
            assert rv.status_code == 200

            # check HTML consistency
            self.assertIn(b'Message', rv.data)

    # # # # # # # # # # try to select two existing users # # # # # # # # # #
    def test_two_users_selection(self):
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
            assert b'tester' in rv.data
            # create a possible recipient
            rv = create_user(
                tested_app,
                "first_recipient@example.com",
                "firstname1",
                "lastname1",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200
            assert b'firstname1' in rv.data
            # create a second possible recipient
            rv = create_user(
                tested_app,
                "second_recipient@example.com",
                "firstname2",
                "lastname2",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200
            assert b'firstname2' in rv.data
            # login with the tester user
            response = login(tested_app, 'tester@example.com', 'password')
            self.assertIn(b'Hi tester', response.data)

            # retrieve list_of_recipients.html
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

            # TODO: check presence of first_recipient and second_recipient
            # in the html page

            # selection of a user and POST request
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                    ['first_recipient@example.com',
                     'second_recipient@example.com']},
                follow_redirects=False
            )

            assert rv.status_code == 302
            print(rv.location)
            assert rv.location == "http://localhost/send?data=first_recipient%40example.com%2C+second_recipient%40example.com"
