from flask import Blueprint, render_template
from monolith.database import Notification, db
import flask_login
from flask_login.utils import login_required


alerts = Blueprint('alerts', __name__)


# get user notifications
# noinspection PyUnresolvedReferences
@alerts.route('/notifications', methods=['GET'])
@login_required
def notifications():

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


# return the number of unread notifications for user_email
def get_notifincations_count(user_email):
        query = db.session.query(Notification).\
                filter_by(user_email=user_email, is_read=False)
        notifications_count = query.count()

        return notifications_count
