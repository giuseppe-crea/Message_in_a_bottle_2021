import flask_login
from flask import Blueprint, render_template
from flask_login import login_required

from monolith import lottery as lt

lottery = Blueprint('lottery', __name__)


@lottery.route('/lottery')
@login_required
def lottery_ui():
    """
    Load the lottery interface for the user. It shows the user's points count
    and provides the message unlock feature.
    :return: render lottery.html
    """
    user = flask_login.current_user
    points = lt.get_usr_points(user)
    message = "You have " + str(points) + " lottery points!"
    return render_template("lottery.html", message=message, price=lt.price)


@lottery.route('/lottery/unlock')
@login_required
def unlock():
    """
    Message unlock feature, the user can spend points
    to unlock the next message
    :return: render updated lottery.html
    """
    user = flask_login.current_user
    points = lt.get_usr_points(user)
    unlocked, points = lt.unlock_message(user)
    message = "You have " + str(points) + " lottery points!"
    if unlocked == -1:
        message += "<br> You don't have enough points to unlock a message"
    elif unlocked == 1:
        message += "<br> New unlocked message in inbox!"
    else:
        message += "<br> No message to unlock."
    return render_template("lottery.html", message=message, price=lt.price)
