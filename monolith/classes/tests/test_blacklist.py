import unittest
from monolith.classes.tests.utils import get_testing_app


class TestBlacklist(unittest.TestCase):
    #def __init__(self):
       # super().__init__()
        #self.tested_app = get_testing_app()

    def test_get_empty(self):
        tested_app = get_testing_app()
        # the user logs
        with tested_app:
            login_reply = tested_app.post(
                '/login',
                data={'email': 'default@example.com', 'password': 'admin'},
                follow_redirects=True,
            )
            # expected a correct login
            self.assertEqual(200, login_reply.status_code)
            # the user tries to access his data
            response = tested_app.get('/blacklist')
            self.assertIn(b'empty', response.data)

    def test_add(self):
        tested_app = get_testing_app()
        # the user logs
        with tested_app:
            login_reply = tested_app.post(
                '/login',
                data={'email': 'default@example.com', 'password': 'admin'},
                follow_redirects=True,
            )
            # expected a correct login
            self.assertEqual(200, login_reply.status_code)
            response = tested_app.post('/blacklist/prova@prova.com')
            self.assertIn(b'prova@prova.com blocked', response.data)

            response = tested_app.get('/blacklist')
            self.assertIn(b'prova@prova.com', response.data)

    def test_add_multiple(self):
        tested_app = get_testing_app()
        # the user logs
        with tested_app:
            login_reply = tested_app.post(
                '/login',
                data={'email': 'default@example.com', 'password': 'admin'},
                follow_redirects=True,
            )
            # expected a correct login
            self.assertEqual(200, login_reply.status_code)
            tested_app.post('/blacklist/prova1@prova.com')
            tested_app.post('/blacklist/prova2@prova.com')
            tested_app.post('/blacklist/prova3@prova.com')


            response = tested_app.get('/blacklist')
            self.assertIn(b'prova1@prova.com', response.data)
            self.assertIn(b'prova2@prova.com', response.data)
            self.assertIn(b'prova3@prova.com', response.data)


    def test_delete(self):
        tested_app = get_testing_app()
        # the user logs
        with tested_app:
            login_reply = tested_app.post(
                '/login',
                data={'email': 'default@example.com', 'password': 'admin'},
                follow_redirects=True,
            )
            # expected a correct login
            self.assertEqual(200, login_reply.status_code)
            tested_app.post('/blacklist/prova1@prova.com')
            tested_app.post('/blacklist/prova2@prova.com')
            tested_app.post('/blacklist/prova3@prova.com')

            response = tested_app.delete('/blacklist/prova2@prova.com')
            self.assertIn(b'prova2@prova.com removed', response.data)

            response = tested_app.get('/blacklist')
            self.assertIn(b'prova1@prova.com', response.data)
            self.assertNotIn(b'prova2@prova.com', response.data)
            self.assertIn(b'prova3@prova.com', response.data)
            print(response.data)
