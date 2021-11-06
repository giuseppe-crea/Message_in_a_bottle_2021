from flask import Blueprint, abort, redirect, request
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound
from monolith.background import create_notification
from monolith.database import Message, db
from monolith import send, lottery
from monolith.delete import remove_message, delete_for_receiver, \
    delete_for_sender

from monolith.forms import ForwardForm

box = Blueprint('box', __name__)


# noinspection PyUnresolvedReferences
@box.route("/inbox", methods=["GET"], defaults={'_id': None})
@box.route("/inbox/<_id>", methods=["GET", "DELETE"])
@login_required
def prep_inbox(_id):
    user_mail = current_user.get_email()
    role = '/inbox'
    kwargs = {'status': 2, 'receiver_email': user_mail,
              'visible_to_receiver': True}
    if _id is not None:
        kwargs['id'] = int(_id)
    return get_box(kwargs, role)


@box.route("/outbox", methods=["GET"], defaults={'_id': None})
@box.route("/outbox/<_id>", methods=["GET", "DELETE"])
@login_required
def prep_outbox(_id):
    user_mail = current_user.get_email()
    role = '/outbox'
    kwargs = {'status': 2, 'sender_email': user_mail,
              'visible_to_sender': True}
    if _id is not None:
        kwargs['id'] = int(_id)
    return get_box(kwargs, role)


def get_box(kwargs, role):
    if 'id' in kwargs:
        try:
            message = Message().query.filter_by(**kwargs).one()
            if request.method == "DELETE":
                remove_message(message, role)
                # TODO: redirect to confirmation page
                #  this is actually overwritten by the JS currently
                return redirect(role)
            else:
                notify_sender(message)
                return render_template(
                    'list/box_one.html',
                    message=message,
                    role=role
                )
        except NoResultFound:
            abort(403)
    else:
        messages = Message().query.filter_by(**kwargs)
        pending_messages = None
        if role == '/outbox':
            kwargs['status'] = 1
            pending_messages = Message().query.filter_by(**kwargs)
        return render_template(
            'list/box.html',
            messages=messages,
            pending=pending_messages,
            role=role
        )


# notifies the sender when the receiver opens for the first time a message
def notify_sender(message):
    if not message.is_read:
        # send notification
        timestamp = message.time
        title = message.receiver_email + " Read Your Message"
        description = \
            "<i>" + "\"" + message.message + "\"" + "</i>"
        create_notification(
            title,
            description,
            timestamp,
            message.sender_email
        )
        # set the message as is:read=True
        db.session.query(Message).filter_by(
            id=message.id).update(dict(is_read=True))
        db.session.commit()
    return


@box.route("/inbox/forward/<_id>", methods=["GET", "POST"])
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


@box.route("/outbox/withdraw/<_id>", methods=["GET"])
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
            if message.status == 1:
                delete_for_receiver(message)
                delete_for_sender(message)
                points -= lottery.price
                lottery.set_points(current_user.get_id(), points)
                return redirect('/outbox')
    abort(401)
