from flask import Blueprint, abort, redirect, request
from flask.templating import render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import NoResultFound
from monolith.background import create_notification, LOTTERY_PRICE
from monolith.database import Message, db
from monolith import send
from monolith.delete import remove_message, delete_for_receiver, \
    delete_for_sender

from monolith.forms import ForwardForm, ReplayForm
from monolith.send import send_messages, save_draft
from monolith.views.doc import auto

box = Blueprint('box', __name__)


# noinspection PyUnresolvedReferences
@box.route("/inbox", methods=["GET"], defaults={'_id': None})
@box.route("/inbox/<_id>", methods=["GET", "DELETE"])
@auto.doc(groups=['routes'])
@login_required
def prep_inbox(_id):
    """
    Prepares the query arguments to populate the message list as if the user
    had accessed the inbox functionality
    If the optional message id is passed, the query will return only the
    specific message with that id
    Performs all necessary checks to make sure the user is authorized to view
    a specific message

    :param _id: optional message id
    :return: a rendered view
    """
    user_mail = current_user.get_email()
    role = '/inbox'
    kwargs = {'status': 2, 'receiver_email': user_mail,
              'visible_to_receiver': True}
    if _id is not None:
        kwargs['id'] = int(_id)
    return get_box(kwargs, role)


@box.route("/outbox", methods=["GET"], defaults={'_id': None})
@box.route("/outbox/<_id>", methods=["GET", "DELETE"])
@auto.doc(groups=['routes'])
@login_required
def prep_outbox(_id):
    """
    Prepares the query arguments to populate the message list as if the user
    had accessed the sent messages functionality
    If the optional message id is passed, the query will return only the
    specific message with that id
    Performs all necessary checks to make sure the user is authorized to view
    a specific message

    :param _id: optional message id
    :return: a list of sent messages, divided in delivered and pending
    """
    user_mail = current_user.get_email()
    role = '/outbox'
    kwargs = {'sender_email': user_mail,
              'visible_to_sender': True}
    if _id is not None:
        kwargs['id'] = int(_id)
    return get_box(kwargs, role)


def get_box(kwargs, role):
    """
    returns either the inbox or the outbox, based on the route that was called
    then performs a database query with the prepared arguments for that route
    finally renders everything in a proper page
    works for both a single message and a list of messages
    DELETE will only delete the message for the current user, not their partner

    :param kwargs: query keyword arguments
    :param role: either /inbox or /outbox depending on the route
    :return: a rendered view
    """
    if 'id' in kwargs:
        try:
            message = Message().query.filter_by(**kwargs).one()
            if request.method == "DELETE":
                remove_message(message, role)
                return redirect(role)
            else:
                if role == '/inbox':
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


def notify_sender(message):
    """
    notifies the sender when the receiver opens for the first time a message

    :param message: message object
    :return: a rendered view
    """
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


@box.route("/inbox/forward/<m_id>", methods=["GET", "POST"])
@auto.doc(groups=['routes'])
@login_required
def forward(m_id):
    """
    Implements the forward message feature.

    :param m_id: message id
    :return: a rendered view
    """
    if m_id is not None:
        # get the message from the database
        try:
            user_mail = current_user.get_email()
            message = Message().query.filter_by(
                id=int(m_id),
                receiver_email=user_mail
            ).one()
            # asks the user the email of the new receiver and the delivery time
            form = ForwardForm()
            if form.validate_on_submit():
                address = form.data["recipient"]
                time = form.data["time"]
                # add a forward header to the message
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


@box.route("/outbox/withdraw/<m_id>", methods=["GET"])
@auto.doc(groups=['routes'])
@login_required
def withdraw(m_id):
    """
    Implements the withdraw message feature.
    The user can spend lottery points to withdraw a message.

    :param m_id: message id
    :return: a rendered view
    """
    if m_id is not None:
        # get the user's total lottery points
        points = current_user.get_points()
        if points >= LOTTERY_PRICE:
            # get the message from the database
            message = None
            try:
                message = Message().query.filter_by(
                    sender_email=current_user.email,
                    id=int(m_id)).one()
            except NoResultFound:
                abort(403)
            # check that the message has not already been delivered
            if message.status == 1:
                delete_for_receiver(message)
                delete_for_sender(message)
                # decrease the user's points
                points -= LOTTERY_PRICE
                current_user.set_points(points)
                db.session.commit()
                return redirect('/outbox')
    abort(401)


@box.route("/inbox/replay/<m_id>", methods=["GET", "POST"])
@auto.doc(groups=['routes'])
@login_required
def replay(m_id):
    """
    Implements the replay message feature.

    :param m_id: message id
    :return: a rendered view
    """
    if m_id is None:
        return redirect('/inbox')
    message = None
    # get the massage from the database
    try:
        user_mail = current_user.get_email()
        message = Message().query.filter_by(
            id=int(m_id),
            receiver_email=user_mail
        ).one()
    except NoResultFound:
        abort(403)

    # get the receiver mail from the original message
    receiver = message.sender_email
    # ask the user to insert the text and the delivery date of the replay
    form = ReplayForm()

    # send the replay
    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.data['message']
            time = form.data['time']
            to_parse = receiver.split(', ')
            current_user_mail = getattr(current_user, 'email')
            if request.form.get("save_button"):
                # the user asked to save this message
                save_draft(current_user_mail, receiver, message, time)
                return redirect('/')
            correctly_sent, not_correctly_sent = \
                send_messages(to_parse, current_user_mail, time, message, None)
        else:
            return render_template('error_template.html', form=form)
        return render_template(
            'done_sending.html',
            users1=correctly_sent,
            users2=not_correctly_sent,
            text=message
        )
    else:
        return render_template('send.html', form=form)
