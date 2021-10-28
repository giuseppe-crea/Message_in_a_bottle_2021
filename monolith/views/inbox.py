from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required, current_user
from monolith.database import SentMessage

inbox = Blueprint('inbox', __name__)


@inbox.route("/inbox", methods=["GET"], defaults={'_id': None})
@inbox.route("/inbox/<_id>", methods=["GET"])
@login_required
def _inbox(_id):
    user_mail = current_user.get_email()
    if _id is not None:
        # TODO: also check that mail == user_mail
        message = SentMessage().query.filter_by(id=int(_id)).one()
        return render_template("list/inbox_one.html", message=message)
    else:
        messages = SentMessage().query.filter_by(receiver_email=user_mail)
        return render_template("list/inbox.html", messages=messages)
