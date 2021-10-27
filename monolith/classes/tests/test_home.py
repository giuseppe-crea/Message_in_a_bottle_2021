import unittest
import json
from flask import request, jsonify
from monolith import app
from monolith.classes.tests.utils import get_testing_app


class TestHome(unittest.TestCase):
    def test_homepage(self):
        # start by loading the home as anonymous
        client = app.test_client()
        rv = client.get('/')
        assert b'Hi Anonymous' in rv.data
