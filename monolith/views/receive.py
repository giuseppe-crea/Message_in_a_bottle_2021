
from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required
from monolith.database import db, SentMessage

receive = Blueprint('receive', __name__)

@receive.route("/inbox", methods=["GET"])
@login_required
def inbox():
    messages = SentMessage().query.all()
    return render_template("list/inbox.html", messages = messages)

@receive.route("/inbox/<id>", methods=["GET"])
@login_required
def inbox_id(id):
    message = SentMessage().query.filter_by(id = int(id)).one()
    return render_template("list/inbox_one.html", message = message)

