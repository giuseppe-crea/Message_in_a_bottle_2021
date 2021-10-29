from flask import Blueprint, abort
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith.database import SentMessage

inbox = Blueprint('inbox', __name__)


@inbox.route("/inbox", methods=["GET"], defaults={'_id': None})
@inbox.route("/inbox/<_id>", methods=["GET"])
@login_required
def _inbox(_id):
    user_mail = current_user.get_email()
    if _id is not None:
        try:
            message = SentMessage().query.filter_by(
                id=int(_id),
                receiver_email=user_mail
            ).one()
            return render_template("list/inbox_one.html", message=message)
        except NoResultFound:
            abort(403)
    else:
        messages = SentMessage().query.filter_by(receiver_email=user_mail)
        return render_template("list/inbox.html", messages=messages)
