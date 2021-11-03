from flask import Blueprint, abort, redirect
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith import send, lottery
from monolith.database import Message
from monolith.delete import delete_for_receiver, delete_for_sender
from monolith.forms import ForwardForm

inbox = Blueprint('inbox', __name__)


# noinspection PyUnresolvedReferences
@inbox.route("/inbox", methods=["GET"], defaults={'_id': None})
@inbox.route("/inbox/<_id>", methods=["GET"])
@login_required
def get_inbox(_id):
    user_mail = current_user.get_email()
    if _id is not None:
        try:
            message = Message().query.filter_by(
                id=int(_id),
                receiver_email=user_mail,
                status=2,
                visible_to_receiver=True
            ).one()
            return render_template("list/inbox_one.html", message=message,
                                   price=lottery.price)
        except NoResultFound:
            abort(403)
    else:
        messages = Message().query.filter_by(
            receiver_email=user_mail,
            status=2,
            visible_to_receiver=True
        )
        return render_template("list/inbox.html", messages=messages)


@inbox.route("/inbox_delete/<_id>", methods=["GET"])
@login_required
def delete(_id):
    user_mail = current_user.get_email()
    if _id is not None:
        try:
            message = Message().query.filter_by(
                id=int(_id),
                receiver_email=user_mail,
                status=2,
                visible_to_receiver=True
            ).one()
            # TODO: add confirmation window maybe?
            #  add a successful deletion notification?
            delete_for_receiver(message)
            return redirect('/inbox')
        except NoResultFound:
            abort(403)


@inbox.route("/inbox/forward/<_id>", methods=["GET", "POST"])
@login_required
def forward(_id):
    if _id is not None:
        try:
            user_mail = current_user.get_email()
            message = Message().query.filter_by(
                id=int(_id),
                receiver_email=user_mail
            ).one()
            form = ForwardForm()
            if form.validate_on_submit():
                address = form.data["recipient"]
                time = form.data["time"]
                frw_message = "Forwarded by: " + message.receiver_email
                frw_message += "\nFrom: " + message.sender_email
                frw_message += "\n\n" + message.message
                correctly_sent, not_correctly_sent = \
                    send.send_messages(address.split(', '), user_mail, time,
                                       frw_message, None)
                return render_template(
                    'done_sending.html',
                    users1=correctly_sent,
                    users2=not_correctly_sent,
                    text=frw_message
                )
            return render_template('request_form.html', form=form)
        except NoResultFound:
            abort(403)


@inbox.route("/inbox/withdraw/<_id>", methods=["GET"])
@login_required
def withdraw(_id):
    if _id is not None:
        points = lottery.get_usr_points(current_user.get_id())
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
            return redirect('/inbox')
        else:
            abort(401)
