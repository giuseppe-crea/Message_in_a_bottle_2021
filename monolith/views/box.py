from flask import Blueprint, abort, redirect, request
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound

from monolith import send
from monolith.database import Message
from monolith.forms import ForwardForm
from monolith.delete import remove_message

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
