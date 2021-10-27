
from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required
from monolith.background import deliver_message

receive = Blueprint('receive', __name__)


@receive.route("/inbox", methods=["POST"])
@login_required
def inbox():


    
    return render_template("inbox.html")


@receive.route("/create_done", methods=["POST"])
@login_required
def inbox():


    
    return render_template("inbox.html")    