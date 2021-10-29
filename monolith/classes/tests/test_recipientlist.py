import unittest
from monolith.classes.tests.utils import get_testing_app, create_user, login

# TODO: redundant code everywhere, refine the tested_app handling or make a unique big test function to not repeat the code

class TestRecipientList(unittest.TestCase):

    # # # # # # # # # # # # # test unauthorized access # # # # # # # # # # # # #
    def test_unauthorized_access(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/list_of_recipients')
            assert rv.status_code == 401

    # # # # # # # # # # # # # test page retrieving # # # # # # # # # # # # #
    def test_page_retrieve(self):
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
            self.assertIn(b'Hi tester', response.data)

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
            # tester itself information and admin information
            self.assertIn(b'{"htmlresponse":"<br>\\n<form action=\\"\\" method=\\"POST\\">\\n  <br>\\n  <input type=submit value=\\"Choose Recipients\\">\\n  <br><br>\\n  \\n  <ul id=\\"multiple_field_form\\"><li><input id=\\"multiple_field_form-0\\" name=\\"multiple_field_form\\" type=\\"checkbox\\" value=\\"default@example.com\\"> <label for=\\"multiple_field_form-0\\">Default Admin: default@example.com</label></li><li><input id=\\"multiple_field_form-1\\" name=\\"multiple_field_form\\" type=\\"checkbox\\" value=\\"tester@example.com\\"> <label for=\\"multiple_field_form-1\\">tester tester: tester@example.com</label></li></ul>\\n</form>"}\n', rv.data)

    # # # # # # # # # # # try to select an existing user # # # # # # # # # # #
    def test_searchbox_interaction(self):

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
            self.assertIn(b'Hi tester', response.data)

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
            self.assertIn(b'{"htmlresponse":"<br>\\n<form action=\\"\\" method=\\"POST\\">\\n  <br>\\n  <input type=submit value=\\"Choose Recipients\\">\\n  <br><br>\\n  \\n  <ul id=\\"multiple_field_form\\"></ul>\\n</form>"}\n'
, rv.data)
            assert rv.status_code == 200

            # keyboard input of 't'
            # exists an account with a 't'
            # in his information (tester)
            rv = tested_app.post(
                '/live_search',
                data={'query': 't'},
                follow_redirects=True
            )
            self.assertIn(
                b'{"htmlresponse":"<br>\\n<form action=\\"\\" method=\\"POST\\">\\n  <br>\\n  <input type=submit value=\\"Choose Recipients\\">\\n  <br><br>\\n  \\n  <ul id=\\"multiple_field_form\\"><li><input id=\\"multiple_field_form-0\\" name=\\"multiple_field_form\\" type=\\"checkbox\\" value=\\"default@example.com\\"> <label for=\\"multiple_field_form-0\\">Default Admin: default@example.com</label></li><li><input id=\\"multiple_field_form-1\\" name=\\"multiple_field_form\\" type=\\"checkbox\\" value=\\"tester@example.com\\"> <label for=\\"multiple_field_form-1\\">tester tester: tester@example.com</label></li><li><input id=\\"multiple_field_form-2\\" name=\\"multiple_field_form\\" type=\\"checkbox\\" value=\\"recipient@example.com\\"> <label for=\\"multiple_field_form-2\\">lastname firstname: recipient@example.com</label></li></ul>\\n</form>"}\n'                , rv.data)
            assert rv.status_code == 200

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
            assert response.status_code == 200
            self.assertIn(b'Hi tester', response.data)

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

            # void POST request (no recipient selection)
            rv = tested_app.post(
                '/list_of_recipients',
                data={},
                follow_redirects=True
            )
            assert rv.status_code == 200

            # check HTML consistency
            self.assertIn( b'<!--suppress ALL -->\n\n<html>\n <head>\n     <script>\n         // fill the recipient form input, if necessary\n         function set_recipients(){\n            // retrieve the URL\n            const queryString = window.location.search;\n            // retrieve the string of parameters\n            const urlParams = new URLSearchParams(queryString);\n            // check if data are passed through a GET request\n            if(urlParams.has(\'data\')){\n                // retrieve the value\n                const recipients = urlParams.get(\'data\');\n                // set the input field\n                document.getElementById(\'recipient\').setAttribute(\'value\', recipients);\n            }\n         }\n     </script>\n     <title>Send a Message</title>\n </head>\n <body onload="set_recipients()"> <!-- to set through the DOM the selected recipients passed as GET parameters -->\n  <form action="" method="POST">\n    \n    <dl>\n     \n     <dt><label for="message">Message</label></dt>\n     <dd><input id="message" name="message" required type="text" value=""></dd>\n       \n     \n     <dt><label for="time">Send on</label></dt>\n     <dd><input id="time" name="time" required type="datetime-local" value=""></dd>\n       \n     \n     <dt><label for="recipient">Recipient</label></dt>\n     <dd><input id="recipient" name="recipient" required type="text" value=""></dd>\n       \n     \n    </dl>\n    <p>\n    See a <a href="/list_of_recipients">list</a> of possible recipients\n    <br> <br>\n    <input type=submit value="Send!">\n  </form>\n <a href="/logout">logout</a>\n </body>\n</html>', rv.data)

    def test_single_selection(self):
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
            self.assertIn(b'Hi tester', response.data)

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

            # testing with no redirection
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        'recipient@example.com'},
                follow_redirects=False
            )
            assert rv.status_code == 302
            assert rv.location == "http://localhost/send?data=recipient%40example.com"
            self.assertIn(b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/send?data=recipient%40example.com">/send?data=recipient%40example.com</a>.  If not click the link.', rv.data)

            # testing with redirection
            rv = tested_app.post(
                '/list_of_recipients',
                data={
                    'multiple_field_form':
                        'recipient@example.com'},
                follow_redirects=True
            )
            assert rv.status_code == 200
            self.assertIn( b'<!--suppress ALL -->\n\n<html>\n <head>\n     <script>\n         // fill the recipient form input, if necessary\n         function set_recipients(){\n            // retrieve the URL\n            const queryString = window.location.search;\n            // retrieve the string of parameters\n            const urlParams = new URLSearchParams(queryString);\n            // check if data are passed through a GET request\n            if(urlParams.has(\'data\')){\n                // retrieve the value\n                const recipients = urlParams.get(\'data\');\n                // set the input field\n                document.getElementById(\'recipient\').setAttribute(\'value\', recipients);\n            }\n         }\n     </script>\n     <title>Send a Message</title>\n </head>\n <body onload="set_recipients()"> <!-- to set through the DOM the selected recipients passed as GET parameters -->\n  <form action="" method="POST">\n    \n    <dl>\n     \n     <dt><label for="message">Message</label></dt>\n     <dd><input id="message" name="message" required type="text" value=""></dd>\n       \n     \n     <dt><label for="time">Send on</label></dt>\n     <dd><input id="time" name="time" required type="datetime-local" value=""></dd>\n       \n     \n     <dt><label for="recipient">Recipient</label></dt>\n     <dd><input id="recipient" name="recipient" required type="text" value=""></dd>\n       \n     \n    </dl>\n    <p>\n    See a <a href="/list_of_recipients">list</a> of possible recipients\n    <br> <br>\n    <input type=submit value="Send!">\n  </form>\n <a href="/logout">logout</a>\n </body>\n</html>', rv.data)

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

            # login with the tester user
            response = login(tested_app, 'tester@example.com', 'password')
            assert response.status_code == 200
            self.assertIn(b'Hi tester', response.data)

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

            # create a possible recipient
            rv = create_user(
                tested_app,
                "first_recipient@example.com",
                "firstname",
                "lastname",
                "01/01/2000",
                "password"
            )
            assert rv.status_code == 200

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
            assert rv.location == "http://localhost/send?data=first_recipient%40example.com%2C+second_recipient%40example.com"
            self.assertIn( b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/send?data=first_recipient%40example.com%2C+second_recipient%40example.com">/send?data=first_recipient%40example.com%2C+second_recipient%40example.com</a>.  If not click the link.'
, rv.data)
