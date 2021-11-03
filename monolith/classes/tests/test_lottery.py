import unittest

from monolith.classes.tests import utils
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
