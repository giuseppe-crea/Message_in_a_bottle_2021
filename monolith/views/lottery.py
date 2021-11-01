import flask_login
from flask import Blueprint, render_template
from flask_login import login_required

from monolith import lottery as lt

lottery = Blueprint('lottery', __name__)


@lottery.route('/lottery')
@login_required
def lottery_ui():
    user = flask_login.current_user
    points = lt.get_usr_points(user)
    message = "You have " + str(points) + " lottery points!"
    return render_template("lottery.html", message=message, price=lt.price)


@lottery.route('/lottery/unlock')
@login_required
def unlock():
    user = flask_login.current_user
    points = lt.get_usr_points(user)
    # unlocked, points = lt.unlock_message(user)
    message = "You have " + str(points) + " lottery points!"
    # if unlocked:
    #    message += "<br> New unlocked message in inbox!"
    # else:
    #    message += "<br> No message to unlock."
    message += "<br>Unlock function not implemented."
    return render_template("lottery.html", message=message, price=lt.price)
