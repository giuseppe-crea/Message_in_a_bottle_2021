
import unittest
from monolith.classes.tests.utils import get_testing_app, login, create_user

class TestHome(unittest.TestCase):
    def test_send_message(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = create_user(
                tested_app,
                "sender@example.com",
                "Alice",
                "Alice",
                "01/01/1990",
                "alice")
            assert rv.status_code == 200