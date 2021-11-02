import unittest
from time import sleep

import flask_login

from monolith import lottery
from monolith.classes.tests import utils
from monolith.lottery import Lottery


class DebugLottery(Lottery):
    def __init__(self, period):
        super().__init__()
        self.period = period


class TestLottery(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the testing app for all the tests of the class.
        """
        super(TestLottery, self).__init__(*args, **kwargs)
        self.app = utils.get_testing_app()

    def test_no_points(self):
        with self.app:
            user, psw = "default@example.com", "admin"
            utils.login(self.app, user, psw)
            user = flask_login.current_user
            lottery.set_points(user.get_id(), 0)
            rv = self.app.get("/lottery")
            self.assertIn(b"You have 0 lottery points!", rv.data)

    def test_lottery(self):
        with self.app:
            user, psw = "default@example.com", "admin"
            utils.login(self.app, user, psw)
            user = flask_login.current_user
            lottery.set_points(user.get_id(), 0)
            #iterations = 2
            period = 2
            db_lottery = DebugLottery(period)
            db_lottery.start()
            sleep(period + 1)
            """if not db_lottery.completed:
                sleep(10)"""
            db_lottery.cancel()
            self.assertEqual(True, db_lottery.cancelled)
            self.assertEqual(None, db_lottery.error)
            #expected_points = iterations * lottery.prize
            #expected = "You have " + str(expected_points) + " lottery points!"
            #expected = bytes(expected, 'utf-8')
            rv = self.app.get("/lottery")
            #self.assertIn(expected, rv.data)
            self.assertNotIn(b"You have 0 lottery points!", rv.data)

