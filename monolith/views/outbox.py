from flask import Blueprint, abort, redirect
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith import lottery
from monolith.database import Message
from monolith.delete import delete_for_sender, delete_for_receiver

outbox = Blueprint('outbox', __name__)


@outbox.route("/outbox/withdraw/<_id>", methods=["GET"])
@login_required
def withdraw(_id):
    if _id is not None:
        points = lottery.get_usr_points(current_user)
        if points >= lottery.price:
            message = None
            try:
                message = Message().query.filter_by(
                    id=int(_id)).one()
            except NoResultFound:
                abort(403)
            delete_for_receiver(message)
            delete_for_sender(message)
            points -= lottery.price
            lottery.set_points(current_user.get_id(), points)
            return redirect('/outbox')
        else:
            abort(401)
