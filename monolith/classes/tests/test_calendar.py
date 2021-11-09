import unittest
import datetime
import flask
from monolith.background import deliver_message
from monolith.classes.tests.utils import get_testing_app, login, create_user, \
    create_message


class TestCalendar(unittest.TestCase):
    # a non-authenticated user cannot access his calendar
    def test_unauthorized(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/calendar')
            assert rv.status_code == 401
            rv = tested_app.get('/calendar/sent')
            assert rv.status_code == 401
            rv = tested_app.get('/calendar/received')
            assert rv.status_code == 401

    def test_calendar(self):
        tested_app = get_testing_app()
        with tested_app:
            # create sender
            rv = create_user(
                tested_app,
                "sender@example.com",
                "sender",
                "sender",
                "01/01/1990",
                "sender")
            assert rv.status_code == 200

            # create receiver
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "receiver",
                "receiver",
                "01/01/1990",
                "receiver")
            assert rv.status_code == 200

            # sender logs in
            response = login(tested_app, 'sender@example.com', 'sender')
            assert response.status_code == 200
            # sender can access his calendar
            rv = tested_app.get('/calendar')
            assert rv.status_code == 200
            rv = tested_app.get('/calendar/received')
            assert rv.status_code == 200
            rv = tested_app.get('/calendar/sent')
            assert rv.status_code == 200
            # the message is not present in sender's calendar/sent
            self.assertTrue(
                'Message Sent'
                not in rv.get_data(as_text=True)
                )
            self.assertTrue(
                '<b>To: receiver@example.com</b>'
                not in rv.get_data(as_text=True)
                )
            # sender sends a message to receiver
            delivery_time = datetime.datetime.now()
            message = create_message(
                "Test1",
                "sender@example.com",
                "receiver@example.com",
                delivery_time.strftime('%Y-%m-%dT%H:%M'),
                None,
                1
            )
            deliver_message(flask.current_app, message.get_id())
            # the message is present in sender's calendar/sent
            rv = tested_app.get('/calendar/sent')
            assert rv.status_code == 200
            self.assertTrue('Message Sent' in rv.get_data(as_text=True))
            self.assertTrue(
                '<b>To: receiver@example.com</b>'
                in rv.get_data(as_text=True)
                )
            # the message is not present in sender's calendar/received
            rv = tested_app.get('/calendar/received')
            self.assertTrue(
                'Message Sent'
                not in rv.get_data(as_text=True)
                )
            self.assertTrue(
                '<b>To: receiver@example.com</b>'
                not in rv.get_data(as_text=True)
                )

            # sender logs out
            tested_app.get('/logout')
            # receiver logs in
            response = login(tested_app, 'receiver@example.com', 'receiver')
            assert response.status_code == 200
            # the message is present in receiver's calendar/received
            rv = tested_app.get('/calendar/received')
            assert rv.status_code == 200
            self.assertTrue(
                'Message Received'
                in rv.get_data(as_text=True)
                )
            self.assertTrue(
                '<b>From: sender@example.com</b>'
                in rv.get_data(as_text=True)
                )
            # the message is not present in receiver's calendar/sent
            rv = tested_app.get('/calendar/sent')
            self.assertTrue(
                'Message received'
                not in rv.get_data(as_text=True)
                )
            self.assertTrue(
                '<b>To: receiver@example.com</b>'
                not in rv.get_data(as_text=True)
                )
