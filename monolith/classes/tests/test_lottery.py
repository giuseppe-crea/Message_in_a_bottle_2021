import unittest

import flask
import flask_login
from flask_login import current_user

from monolith.database import db
from monolith.background import lottery_task
from monolith.lottery import prize, price
from monolith.classes.tests.utils import get_testing_app, login, create_ex_usr


class TestLottery(unittest.TestCase):
    """
    Tests for the lottery feature.
    """

    def test_withdraw(self):
        """
        Test the message withdraw feature.
        """
        tested_app = get_testing_app()
        with tested_app:
            # create and log a new user
            user, psw = create_ex_usr(tested_app)
            rv = login(tested_app, user, psw)
            assert rv.status_code == 200
            # give some points to the user
            current_user.add_points(200)
            current_points = current_user.get_points()
            db.session.commit()
            # send a message from user to default user
            tested_app.post(
                '/send',
                data={
                    'message': "Short test message",
                    'recipient': "example@example.com",
                    'time': "2030-01-01T01:01"},
                follow_redirects=True
            )
            # the message is in the outbox
            rv = tested_app.get("/outbox")
            self.assertIn(b"example@example.com", rv.data)

            # withdraw the message
            rv = tested_app.get("/outbox/withdraw/1")
            print(rv.data)
            self.assertEqual(rv.status_code, 302)

            # message removed from outbox
            rv = tested_app.get("/outbox")
            self.assertNotIn(b"example@example.com", rv.data)

            assert current_user.get_points() == current_points - price

    def test_lottery_task(self):
        app = get_testing_app()
        with app:
            email, psw = "example@example.com", "admin"
            login(app, email, psw)
            user = flask_login.current_user
            # should be 1000, but it doesn't matter
            starting_points = user.get_points()
            lottery_task(flask.current_app)
            rv = app.get('/user_data')
            print(rv.data)
            assert bytes(str(starting_points + prize), 'utf-8') in rv.data
