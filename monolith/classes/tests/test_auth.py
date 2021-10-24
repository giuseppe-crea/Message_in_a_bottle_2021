
"""
import unittest
import json
from flask import request, jsonify
from monolith import app

class testAuth(unittest.TestCase):
    def test_login(self):
        tested_app = app.test_client()
        # testing that the login page loads
        login_reply = tested_app.get("/login")
        self.assertEqual(login_reply.status_code, 200)
        # test a correct login
        response = tested_app.post(
            '/login',
            data=dict(email="exampl4@example.com", password="admin", login_form=""),
            follow_redirects=True
        )
        self.assertIn(b'Hi Admin!', response.data)

"""