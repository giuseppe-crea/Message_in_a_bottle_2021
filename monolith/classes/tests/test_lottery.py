import unittest

import flask_login

from monolith import lottery
from monolith.classes.tests import utils
from monolith.classes.tests.utils import get_testing_app
from monolith.lottery import Lottery


class DebugLottery(Lottery):
    """
    Subclass of Lottery,
    provides additional functionalities for testing and debug"
    """

    def __init__(self, app, period):
        super().__init__(app)
        self.period = period


class TestLottery(unittest.TestCase):
    """
    Tests for the lottery feature.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the testing app for all the tests of the class.
        """
        super(TestLottery, self).__init__(*args, **kwargs)
        self.app = utils.get_testing_app()

    def test_withdraw(self):
        """
        Test the message withdraw functionality.
        """
        tested_app = get_testing_app()
        with tested_app:
            # create and log a new user
            user, psw = utils.create_ex_usr(tested_app)
            utils.login(tested_app, user, psw)
            user = flask_login.current_user
            # give some points to the user
            lottery.set_points(user.get_id(), lottery.price * 2)

            # send a message from user to default user
            rv = tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "default@example.com",
                    'time': "2030-01-01T01:01"},
                follow_redirects=True
            )
            # the message is in the outbox
            rv = tested_app.get("/outbox")
            self.assertIn(b"default@example.com", rv.data)

            # withdraw the message
            rv = tested_app.get("/outbox/withdraw/1")
            self.assertEqual(rv.status_code, 302)

            # message removed from outbox
            rv = tested_app.get("/outbox")
            self.assertNotIn(b"default@example.com", rv.data)


"""
def test_lottery(self):
    period = 2
    db_lottery = DebugLottery(self.app, period)
    db_lottery.start()
    with self.app:
        user, psw = "default@example.com", "admin"
        utils.login(self.app, user, psw)
        user = flask_login.current_user
        lottery.set_points(user.get_id(), 0)
        #iterations = 2

        sleep(period + 1)

        db_lottery.cancel()
        self.assertEqual(True, db_lottery.cancelled)
        self.assertEqual(None, db_lottery.error)
        #expected_points = iterations * lottery.prize
        #expected = "You have " + str(expected_points) + " lottery points!"
        #expected = bytes(expected, 'utf-8')
        rv = self.app.get("/lottery")
        #self.assertIn(expected, rv.data)
        self.assertNotIn(b"You have 0 lottery points!", rv.data)
"""
