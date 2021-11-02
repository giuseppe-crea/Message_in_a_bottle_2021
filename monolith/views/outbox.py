from flask import Blueprint, abort, redirect
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith.delete import delete_for_sender
from monolith.database import Message

outbox = Blueprint('outbox', __name__)


@outbox.route("/outbox", methods=["GET"], defaults={'_id': None})
@outbox.route("/outbox/<_id>", methods=["GET"])
@login_required
def get_outbox(_id):
    user_mail = current_user.get_email()
    if _id is None:
        pending = Message().query.filter_by(
            sender_email=user_mail,
            status=1,
            visible_to_sender=True
        )
        delivered = Message().query.filter_by(
            sender_email=user_mail,
            status=2,
            visible_to_sender=True
        )
        # noinspection PyUnresolvedReferences
        return render_template(
            "list/outbox.html",
            pending=pending,
            delivered=delivered
        )
    if _id is not None:
        try:
            message = Message().query.filter_by(
                id=int(_id),
                sender_email=user_mail
            ).one()
            # noinspection PyUnresolvedReferences
            return render_template("list/outbox_one.html", message=message)
        except NoResultFound:
            abort(403)


@outbox.route("/outbox_delete/<_id>", methods=["GET"])
@login_required
def delete(_id):
    user_mail = current_user.get_email()
    if _id is not None:
        try:
            message = Message().query.filter_by(
                id=int(_id),
                sender_email=user_mail,
                visible_to_sender=True
            ).one()
            # TODO: add confirmation window maybe?
            #  add a successful deletion notification?
            delete_for_sender(message)
            return redirect('/outbox')
        except NoResultFound:
            abort(403)
    abort(404)
