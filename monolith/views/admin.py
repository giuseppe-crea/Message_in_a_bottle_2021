from flask import Blueprint, render_template
from flask_login import login_required
import flask_login
from monolith.auth import admin_required
from monolith.views.alerts import get_notifincations_count


admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET'])
@login_required
@admin_required
def placeholder():

    current_user = flask_login.current_user
    current_user_email = current_user.email
    notifications_count = get_notifincations_count(current_user_email)

    # noinspection PyUnresolvedReferences
    return render_template("index.html", notifications=notifications_count)
