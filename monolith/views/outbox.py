from flask import Blueprint, abort
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith.database import SentMessage

outbox = Blueprint('outbox', __name__)


@outbox.route("/outbox", methods=["GET"], defaults={'_id': None})
@outbox.route("/outbox/<_id>", methods=["GET"])
@login_required
def _outbox(_id):
    user_mail = current_user.get_email()
    if _id is None:
        messages = SentMessage().query.filter_by(sender_email=user_mail)
        # noinspection PyUnresolvedReferences
        return render_template("list/outbox.html", messages=messages)
    if _id is not None:
        try:
            message = SentMessage().query.filter_by(
                id=int(_id),
                sender_email=user_mail
            ).one()
            # noinspection PyUnresolvedReferences
            return render_template("list/outbox_one.html", message=message)
        except NoResultFound:
            abort(403)
