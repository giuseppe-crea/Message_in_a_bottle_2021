import unittest

import flask_login

from monolith import lottery
from monolith.classes.tests import utils


class TestLottery(unittest.TestCase):
    """
    Tests for the lottery feature.
    """

    # TODO move the method and reactivete the test
    """def test_withdraw(self):
        
        Test the message withdraw functionality.
        
        tested_app = get_testing_app()
        with tested_app:
            # create and log a new user
            user, psw = utils.create_ex_usr(tested_app)
            utils.login(tested_app, user, psw)
            user = flask_login.current_user
            # give some points to the user
            lottery.set_points(user.get_id(), lottery.price * 2)

            # send a message from user to default user
            tested_app.post(
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
            self.assertNotIn(b"default@example.com", rv.data)"""

    def test_lottery(self):
        """
        Test the lottery execution
        """
        app = utils.get_testing_app()
        with app:
            # log the default and unique user
            email, psw = "example@example.com", "admin"
            utils.login(app, email, psw)
            user = flask_login.current_user
            # set the user's points to 0
            lottery.set_points(user.get_id(), 0)

            # execute a lottery round
            lottery.execute()

            # expect non zero lottery points
            points = lottery.get_usr_points(user)
            self.assertNotEqual(points, 0)
