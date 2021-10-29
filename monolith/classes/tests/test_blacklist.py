import unittest

from monolith.classes.tests import utils
from monolith.views.blacklist import _is_blacklisted


class TestBlacklist(unittest.TestCase):
    """
    Test class for the blacklist functionalities.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the testing app for all the tests of the class.
        """
        super(TestBlacklist, self).__init__(*args, **kwargs)
        self.app = utils.get_testing_app()

    def _add_user(self, email):
        """
        Add a user to the blacklist of the current logged user
        :param email: the email to block
        """
        self.app.post(
            '/blacklist/add',
            data={'email': email},
            follow_redirects=True, )

    def test_get_empty(self):
        """
        Test the blacklist for a new user.
        """
        with self.app:
            # create a new user
            email, psw = utils.create_ex_usr(self.app)
            # the new user logs
            utils.login(self.app, email, psw)
            # get the blacklist and expect that it is empty
            response = self.app.get('/blacklist')
            self.assertIn(b'empty', response.data)

    def test_add(self):
        """
        Test blacklist insertion.
        """
        with self.app:
            # create a new user
            email, psw = utils.create_ex_usr(self.app)
            # the user logs
            utils.login(self.app, email, psw)
            # create a second user
            email, _ = utils.create_ex_usr(self.app)

            # the logged user add the second to his blacklist
            self.app.post('/blacklist/add',
                          data={'email': email},
                          follow_redirects=True, )

            # get the blacklist and expect that the second user is present
            response = self.app.get('/blacklist')
            self.assertIn(bytes(email, 'utf-8'), response.data)

    def test_add_multiple(self):
        """
        Test multiple insertions in the blacklist.
        """
        # the user logs
        with self.app:
            # create a new user
            email, psw = utils.create_ex_usr(self.app)
            # the user logs
            utils.login(self.app, email, psw)

            # create some new users and add them to the blacklist
            users = utils.create_ex_users(self.app, 5)
            for e, _ in users:
                self._add_user(e)

            # get the blacklist and expect that blocked users are present
            response = self.app.get('/blacklist')
            for e, _ in users:
                self.assertIn(bytes(e, 'utf-8'), response.data)

    def test_delete(self):
        """
        Test deletion from the blacklist.
        """
        with self.app:
            # create a new user
            email, psw = utils.create_ex_usr(self.app)
            # the user logs
            utils.login(self.app, email, psw)
            # create some new users and add them to the blacklist
            users = utils.create_ex_users(self.app, 5)
            for e, _ in users:
                self._add_user(e)

            # get the second user from the list and
            # remove it from the blacklist.
            email, _ = users.pop(2)
            self.app.post('/blacklist/remove',
                          data={'email': email},
                          follow_redirects=True, )

            # get the blacklist and expect that blocked users are present
            response = self.app.get('/blacklist')

            for e, _ in users:
                self.assertIn(bytes(e, 'utf-8'), response.data)

            # and the removed user is not present
            self.assertNotIn(bytes(email, 'utf-8'), response.data)

    def test_wrong_add(self):
        """
        Test forbidden insertions.
        """
        with self.app:
            # create a new user
            email, psw = utils.create_ex_usr(self.app)
            # the user logs
            utils.login(self.app, email, psw)

            # the user tries to insert itself
            self.app.post('/blacklist/add',
                          data={'email': email},
                          follow_redirects=True, )
            # expect that it is not present
            response = self.app.get('/blacklist')
            self.assertNotIn(bytes(email, 'utf-8'), response.data)

            # the user tries to insert a not existing user
            email = "not_exist@example.com"
            self.app.post('/blacklist/add',
                          data={'email': email},
                          follow_redirects=True, )

            # expect that it is not present
            response = self.app.get('/blacklist')
            self.assertNotIn(bytes(email, 'utf-8'), response.data)

    def test_blacklist_check(self):
        """
        Test the internal view.blacklist._is_blacklisted function
        """

        with self.app:
            # create a new user
            receiver, psw = utils.create_ex_usr(self.app)
            # the user logs
            utils.login(self.app, receiver, psw)
            # create a second user
            sender, _ = utils.create_ex_usr(self.app)

            self._add_user(sender)

            self.assertEqual(_is_blacklisted(sender, receiver), True)
            self.assertEqual(_is_blacklisted(receiver, sender), False)
