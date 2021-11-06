from flask import Blueprint, render_template
from monolith.auth import current_user
from monolith.views.alerts import get_notifications_count
from monolith.views.doc import auto

home = Blueprint('home', __name__)


# noinspection PyUnresolvedReferences
@home.route('/')
@auto.doc(groups=['routes'])
def index():
    """
    Homepage view

    :return: a rendered view
    """
    if current_user is not None and hasattr(current_user, 'id'):
        current_user_email = current_user.email
        notifications_count = get_notifications_count(current_user_email)
    else:
        notifications_count = 0

    return render_template("index.html", notifications=notifications_count)
