import unittest
import datetime
from time import sleep

import flask
import flask_login

from monolith import lottery
from monolith.background import deliver_message
from monolith.classes.tests import utils
from monolith.classes.tests.utils import create_message
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

    def test_no_points(self):
        """
        Test the correct response to a user that have no lottery points
        """
        with self.app:
            user, psw = "default@example.com", "admin"
            utils.login(self.app, user, psw)
            user = flask_login.current_user
            # set zero point for thee default users
            lottery.set_points(user.get_id(), 0)
            # get the lottery page of the default user and expect 0 points
            rv = self.app.get("/lottery")
            self.assertIn(b"You have 0 lottery points!", rv.data)
            # request to unlock a message and expect an error
            rv = self.app.get("/lottery/unlock")
            self.assertIn(b"You don't have enough points "
                          b"to unlock a message", rv.data)

    def test_points(self):
        """
        Test the correct response to a user that have points
        """
        with self.app:
            user, psw = "default@example.com", "admin"
            utils.login(self.app, user, psw)
            user = flask_login.current_user
            # set 10 point for thee default users
            lottery.set_points(user.get_id(), 10)
            # get the lottery page of the default user and expect 10 points
            rv = self.app.get("/lottery")
            self.assertIn(b"You have 10 lottery points!", rv.data)


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

    """def test_unlock(self):
        
        Test the message unlock feature
        
        with self.app:
            # create and log a new user
            user, psw = utils.create_ex_usr(self.app)
            utils.login(self.app, user, psw)
            user = flask_login.current_user

            # give some points to the user
            lottery.set_points(user.get_id(), lottery.price * 2)

            # internally send a message to user2 from default user
            delivery_time = datetime.datetime(year=2030, month=3,day=12,
                                              hour=12, minute=30)
            message = create_message(
                "Test1",
                "default@example.com",
                user,
                delivery_time.strftime('%Y-%m-%dT%H:%M'),
                None,
                1
            )
            deliver_message(
                flask.current_app,
                message.get_id()
            )

            message = bytes("You have " + str(lottery.price) +
                            " lottery points!", 'utf-8')

            # unlock the message and expect it is unlocked
            rv = self.app.get("/lottery/unlock")
            self.assertIn(b"New unlocked message in inbox!", rv.data)

            # expect the user's points count updated
            self.assertIn(message, rv.data)

            # expect the unlocked message in the inbox
            rv = self.app.get("/inbox")
            self.assertIn(b"default@example.com", rv.data)
            """




