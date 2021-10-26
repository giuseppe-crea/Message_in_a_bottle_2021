import unittest
from monolith.classes.tests.utils import get_testing_app, create_user, login


class TestRecipientList(unittest.TestCase):

    # # # # # # # # # # # # # # # test page retrieving # # # # # # # # # # # # # # #
    def test_get_list_of_recipients(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 200

    # # # # # # # # # # # # try to select an existing user and see it in send.html page # # # # # # # # # # # #
    def test_user_selection(self):
        tested_app = get_testing_app()
        with tested_app:

            # create a user which will look for the list of available recipients
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
                data={'radio_form': 'recipient@example.com'},
                follow_redirects=True
            )

            assert rv.status_code == 200

            # check HTML consistency
            self.assertIn(b'You can write to: recipient@example.com', rv.data)

    # # # # # # # # # # # # # # # test the submitting of a void form # # # # # # # # # # # # # # #
    def test_no_selection(self):
        tested_app = get_testing_app()
        with tested_app:

            # create a user which will look for the list of available recipients
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
