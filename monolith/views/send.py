from datetime import datetime

from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required
from sqlalchemy.exc import NoResultFound

from monolith.auth import current_user
from monolith.database import Draft, SentMessage
from monolith.forms import SendForm, ReplayForm
from monolith.send import send_messages, save_draft

send = Blueprint('send', __name__)


# noinspection PyUnusedLocal,PyUnboundLocalVariable
@send.route('/send', methods=['POST', 'GET'], defaults={'_id': None})
@send.route('/send/<_id>', methods=['POST', 'GET'])
@login_required
# data is a default parameter used for recipient setting
def _send(_id, data=""):
    form = SendForm()
    if _id is not None and request.method == 'GET':
        # we are viewing a draft, load it after checking its existence
        try:
            draft = Draft().query.filter_by(
                id=int(_id),
                sender_email=current_user.email
            ).one()
        except NoResultFound:
            abort(404)
        form.message.data = draft.message
        form.recipient.data = draft.recipients
        form.time.data = \
            datetime.strptime(draft.delivery_date, '%Y-%m-%d %H:%M:%S')
    correctly_sent = []
    not_correctly_sent = []
    if request.method == 'POST':
        if form.validate_on_submit():
            message, user_input = \
                form.data['message'], form.data['recipient']
            time = form.data['time']
            to_parse = user_input.split(', ')
            current_user_mail = getattr(current_user, 'email')
            if request.form.get("save_button"):
                # the user asked to save this message
                save_draft(current_user_mail, user_input, message, time)
                return redirect('/')
            correctly_sent, not_correctly_sent = \
                send_messages(to_parse, current_user_mail, time, message)
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


@send.route('/send_draft_list', methods=['GET'])
@login_required
def get_message():
    drafts = Draft().query.filter_by(sender_email=current_user.email).all()
    return render_template('list/draft_list.html', drafts=drafts)


@send.route("/send/replay/<_id>", methods=["GET", "POST"])
@login_required
def replay(_id):
    if _id is None:
        return redirect('/inbox')
    message = None
    try:
        user_mail = current_user.get_email()
        message = SentMessage().query.filter_by(
            id=int(_id),
            receiver_email=user_mail
        ).one()
    except NoResultFound:
        abort(403)
    user_input = message.sender_email
    form = ReplayForm()

    correctly_sent = []
    not_correctly_sent = []
    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.data['message']
            time = form.data['time']
            to_parse = user_input.split(', ')
            current_user_mail = getattr(current_user, 'email')
            if request.form.get("save_button"):
                # the user asked to save this message
                save_draft(current_user_mail, user_input, message, time)
                return redirect('/')
            correctly_sent, not_correctly_sent = \
                send_messages(to_parse, current_user_mail, time, message)
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
