from flask import Blueprint, render_template
from flask_login import login_required, current_user
from monolith.database import db, Message
from monolith.views.doc import auto


calendar = Blueprint('calendar', __name__)


def get_sent_messages(user):
    """
    :param user: the user for which to fetch messages
    :return: query of all messages sent from this user and already received
    :rtype: SQLAlchemy.session.query
    """
    sent_messages = db.session.query(Message).filter_by(
        sender_email=user,
        status=2,
        visible_to_sender=True
        )
    return sent_messages


def get_received_messages(user):
    """
    :param user: the user for which to fetch messages
    :return: query of all messages received from this user
    :rtype: SQLAlchemy.session.query
    """
    received_messages = db.session.query(Message).filter_by(
        receiver_email=user,
        status=2,
        visible_to_receiver=True
        )
    return received_messages


@calendar.route('/calendar', methods=['GET'])
@auto.doc(groups=['routes'])
@login_required
def get_calendar():
    """
    Displays messages in a calendar

    :return: a rendered view
    """
    user_email = current_user.get_email()
    user_sent_messages = get_sent_messages(user_email)
    user_received_messages = get_received_messages(user_email)

    return render_template('calendar.html',
                           sent_messages=user_sent_messages,
                           received_messages=user_received_messages)


@calendar.route('/calendar/sent', methods=['GET'])
@auto.doc(groups=['routes'])
@login_required
def get_calendar_sent():
    """
    Calendar view for sent messages only

    :return: a rendered view
    """
    user_email = current_user.get_email()
    user_sent_messages = get_sent_messages(user_email)

    return render_template('calendar.html', sent_messages=user_sent_messages)


@calendar.route('/calendar/received', methods=['GET'])
@auto.doc(groups=['routes'])
@login_required
def get_calendar_received():
    """
    Calendar view for received messages only

    :return: a rendered view
    """
    user_email = current_user.get_email()
    user_received_messages = get_received_messages(user_email)

    return render_template('calendar.html',
                           received_messages=user_received_messages)
