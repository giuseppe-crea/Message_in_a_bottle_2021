import unittest
from monolith import app


class TestHome(unittest.TestCase):
    def test_homepage(self):
        # start by loading the home as anonymous
        client = app.test_client()
        rv = client.get('/')
        assert b'Hi Anonymous' in rv.data
