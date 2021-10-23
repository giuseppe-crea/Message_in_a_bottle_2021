import unittest
import json
from flask import request, jsonify
from monolith import app
from monolith.classes.tests.utils import get_testing_app


class testAuth(unittest.TestCase):
    def test_login(self):
        tested_app = get_testing_app()
        # testing that the login page loads
        login_reply = tested_app.get("/login")
        self.assertEqual(login_reply.status_code, 200)
        # test a correct login
        response = tested_app.post(
            '/login',
            data=dict(email="example@example.com", password="admin", login_form=""),
            follow_redirects=True
        )
        self.assertIn(b'Hi Admin!', response.data)

    def test_login_fail(self):
        tested_app = get_testing_app()
        # testing that the login page loads
        login_reply = tested_app.get("/login")
        self.assertEqual(login_reply.status_code, 200)
        # test a correct login
        response = tested_app.post(
            '/login',
            data=dict(email="example@example.com", password="1234", login_form=""),
            follow_redirects=True
        )
        self.assertNotIn(b'Hi Admin!', response.data)

        response = tested_app.post(
            '/login',
            data=dict(email="admin@example.com", password="admin", login_form=""),
            follow_redirects=True
        )
        self.assertNotIn(b'Hi Admin!', response.data)
