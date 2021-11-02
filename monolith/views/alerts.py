from flask import Blueprint, render_template, request, abort
from werkzeug.utils import redirect
from monolith.database import Notification, db, User
import flask_login
from flask_login.utils import login_required
from datetime import datetime


alerts = Blueprint('alerts', __name__)

def create_alert():
    
    notification = Notification()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notification.add_notification(
        "example@example.com",
                "title1",
                "description",
                timestamp,
                False
                )
  
    db.session.add(notification)
    db.session.commit()

    return 

# get user notifications
# noinspection PyUnresolvedReferences
@alerts.route('/notifications', methods=['GET'])
@login_required
def notifications():

    create_alert()
    create_alert()

    current_user = flask_login.current_user
    current_user_email = current_user.email
    
    # clean read notifications
    db.session.query(Notification).filter_by(user_email=current_user_email,
                                             is_read=True).delete()
    # load unread notifications
    query_notifications = db.session.query(Notification).filter_by \
            (user_email=current_user_email).order_by(Notification.id.desc())
    # set notifications as read
    db.session.query(Notification).filter_by \
           (user_email=current_user_email).update(dict(is_read=True))
    db.session.commit()

    return render_template("notifications.html",
                            notifications=query_notifications)
