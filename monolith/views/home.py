from flask import Blueprint, render_template
from monolith.database import Notification, db
from monolith.auth import current_user

home = Blueprint('home', __name__)


# noinspection PyUnresolvedReferences
@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):

        current_user_email = current_user.email
        query = db.session.query(Notification).filter_by(user_email=\
                current_user_email, is_read=False)
        notifications_count = query.count()
    else:
        notifications_count = 0

    return render_template("index.html", notifications=notifications_count)
