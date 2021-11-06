import unittest
import datetime
import flask
from monolith.background import deliver_message
from monolith.classes.tests.utils import get_testing_app, login, create_user, \
    create_message


class TestNotifications(unittest.TestCase):

    # a non-authenticated user cannot access notifications
    def test_unauthorized(self):
        tested_app = get_testing_app()
        with tested_app:
            rv = tested_app.get('/notifications')
            assert rv.status_code == 401

    # received message notification
    def test_report_received(self):
        tested_app = get_testing_app()
        with tested_app:

            # create the sender account
            rv = create_user(
                tested_app,
                "sender@example.com",
                "sender",
                "sender",
                "01/01/1990",
                "sender")
            assert rv.status_code == 200

            # create the receiver account
            rv = create_user(
                tested_app,
                "receiver@example.com",
                "receiver",
                "receiver",
                "01/01/1990",
                "receiver")
            assert rv.status_code == 200

            # receiver logs in
            response = login(tested_app, 'receiver@example.com', 'receiver')
            assert response.status_code == 200
            # receiver can access his notifications
            rv = tested_app.get('/notifications')
            assert rv.status_code == 200
            # the message is not present in receiver's notifications
            self.assertTrue(
                'sender@example.com Sent You a Message'
                not in rv.get_data(as_text=True)
                )
            # receiver logs out
            tested_app.get('/logout')

            # sender logs in
            response = login(tested_app, 'sender@example.com', 'sender')
            assert response.status_code == 200
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
            deliver_message(
                flask.current_app,
                message.get_id()
            )
            # sender logs out
            tested_app.get('/logout')

            # receiver logs in
            response = login(tested_app, 'receiver@example.com', 'receiver')
            assert response.status_code == 200
            # the message is present in receiver's notifications
            rv = tested_app.get('/notifications')
            assert rv.status_code == 200
            self.assertTrue(
                'sender@example.com Sent You a Message'
                in rv.get_data(as_text=True)
                )

    # (first time only) read message notification
    def test_report_read(self):
        tested_app = get_testing_app()
        with tested_app:

            # create the sender account
            rv = create_user(
                tested_app,
                "sender@example.com",
                "sender",
                "sender",
                "01/01/1990",
                "sender")
            assert rv.status_code == 200

            # create the receiver account
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
            # sender can access his notifications
            rv = tested_app.get('/notifications')
            assert rv.status_code == 200
            # the message is not present in sender's notifications
            self.assertTrue(
                'receiver@example.com Read Your Message'
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
            deliver_message(
                flask.current_app,
                message.get_id()
            )
            # sender logs out
            tested_app.get('/logout')
            # receiver logs in
            response = login(tested_app, 'receiver@example.com', 'receiver')
            assert response.status_code == 200
            # receiver reads the message
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            # receiver logs out
            tested_app.get('/logout')
            # sender logs in
            response = login(tested_app, 'sender@example.com', 'sender')
            assert response.status_code == 200
            # the message is present in sender's notifications
            rv = tested_app.get('/notifications')
            self.assertTrue(
                'receiver@example.com Read Your Message'
                in rv.get_data(as_text=True)
                )

            # now we check that only the first time a notification is sent
            # sender logs out
            tested_app.get('/logout')
            # receiver logs in
            response = login(tested_app, 'receiver@example.com', 'receiver')
            assert response.status_code == 200
            # receiver reads again the message
            rv = tested_app.get('/inbox/1', follow_redirects=True)
            # receiver logs out
            tested_app.get('/logout')
            # sender logs in
            response = login(tested_app, 'sender@example.com', 'sender')
            assert response.status_code == 200
            # the message is not present in sender's notifications
            rv = tested_app.get('/notifications')
            self.assertTrue(
                'receiver@example.com Read Your Message'
                not in rv.get_data(as_text=True)
                )
