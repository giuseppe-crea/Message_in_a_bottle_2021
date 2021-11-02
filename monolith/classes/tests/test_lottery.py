import unittest
from time import sleep

from monolith import lottery
from monolith.classes.tests import utils
from monolith.lottery import Lottery


class DebugLottery(Lottery):
    def __init__(self, period, iterations):
        super().__init__()
        self.max_iter = iterations
        self.period = period
        self.current_iter = 0
        self.completed = False
"""
    def _iter(self):
        print("ITER")
        if self.current_iter >= self.max_iter:
            print("COMPLETE")
            self.completed = True
            self.cancelled = True
            return
        self.current_iter += 1
        super()._iter()
"""

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

            rv = self.app.get("/lottery")
            self.assertIn(b"You have 0 lottery points!", rv.data)

    def test_lottery(self):
        with self.app:
            user, psw = "default@example.com", "admin"
            utils.login(self.app, user, psw)
            iterations = 3
            period = 2
            db_lottery = DebugLottery(period=period, iterations=iterations)
            db_lottery.start()
            sleep(iterations*period + 1)
            """if not db_lottery.completed:
                sleep(10)"""
            print("Current iter" + str(db_lottery.current_iter))
            self.assertEqual(True, db_lottery.cancelled)

            expected_points = iterations * lottery.prize
            expected = "You have " + str(expected_points) + " lottery points!"
            expected = bytes(expected, 'utf-8')
            rv = self.app.get("/lottery")
            #self.assertIn(expected, rv.data)
            self.assertNotIn(b"You have 0 lottery points!", rv.data)
            db_lottery.cancel()
