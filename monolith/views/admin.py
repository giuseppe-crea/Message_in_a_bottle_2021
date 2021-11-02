from flask import Blueprint, render_template
from flask_login import login_required
import flask_login
from monolith.auth import admin_required
from monolith.database import Notification, db


admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
@login_required
@admin_required
def placeholder():

        current_user = flask_login.current_user
        current_user_email = current_user.email
        query = db.session.query(Notification).filter_by(user_email=
                current_user_email, is_read=False)
        notifications_count = query.count()

        return render_template("index.html", notifications=notifications_count)
