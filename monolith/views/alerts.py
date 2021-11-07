from flask import Blueprint, render_template
from monolith.database import Notification, db
import flask_login
from flask_login.utils import login_required
from monolith.views.doc import auto


alerts = Blueprint('alerts', __name__)


# noinspection PyUnresolvedReferences
@alerts.route('/notifications', methods=['GET'])
@auto.doc(groups=['routes'])
@login_required
def notifications():
    """
    Displays the currently pending user notifications

    :return: a rendered view
    """
    current_user = flask_login.current_user
    current_user_email = current_user.email

    # clean read notifications
    db.session.query(Notification).filter_by(user_email=current_user_email,
                                             is_read=True).delete()
    # load unread notifications
    query_notifications = db.session.query(Notification).filter_by(
            user_email=current_user_email).order_by(Notification.id.desc())
    # set notifications as read
    db.session.query(Notification).filter_by(
           user_email=current_user_email).update(dict(is_read=True))
    db.session.commit()

    return render_template("notifications.html",
                           notifications=query_notifications)


# return
def get_notifications_count(user_email):
    """
    :param user_email: the mail we want notification count for
    :return: the number of unread notifications for user_email
    """
    query = db.session.query(Notification).filter_by(
        user_email=user_email,
        is_read=False
    )
    notifications_count = query.count()
    return notifications_count
