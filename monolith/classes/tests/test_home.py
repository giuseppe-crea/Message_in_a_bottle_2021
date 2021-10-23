import unittest
import json
from flask import request, jsonify
from monolith import app
from monolith.classes.tests.utils import get_testing_app


class TestHome(unittest.TestCase):
    def test_my_view(self):
        tested_app = get_testing_app()
        home_reply = tested_app.get("/")

        #body = json.loads(str(home_reply.data, "utf8"))
        return 1
