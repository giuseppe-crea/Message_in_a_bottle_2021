import os
from datetime import datetime

import flask
from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required
from sqlalchemy.exc import NoResultFound
from werkzeug.utils import secure_filename

from monolith.auth import current_user
from monolith.database import Message
from monolith.forms import SendForm, ReplayForm
from monolith.send import send_messages, save_draft, allowed_file

send = Blueprint('send', __name__)


# noinspection PyUnusedLocal,PyUnboundLocalVariable
@send.route('/send', methods=['POST', 'GET'], defaults={'_id': None})
@send.route('/send/<_id>', methods=['POST', 'GET'])
@login_required
# data is a default parameter used for recipient setting
def _send(_id, data=""):
    form = SendForm()
    # if we are loading a draft:
    # the method check is required to avoid resetting the data on a POST
    if _id is not None and request.method == 'GET':
        # load it after checking its existence
        # drafts don't save images
        try:
            draft = Message().query.filter_by(
                id=int(_id),
                sender_email=current_user.email,
                status=0
            ).one()
        except NoResultFound:
            abort(404)
        form.message.data = draft.message
        form.recipient.data = draft.receiver_email
        form.time.data = \
            datetime.strptime(draft.time, '%Y-%m-%d %H:%M:%S')
    # instantiate arrays of mail addresses to display for our sender
    correctly_sent = []
    not_correctly_sent = []
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user_mail = getattr(current_user, 'email')
            file_path = None
            # grab must-have data which we are guaranteed to have
            message, user_input = form.data['message'], form.data['recipient']
            time = form.data['time']
            to_parse = user_input.split(', ')
            # we are saving a draft
            if request.form.get("save_button"):
                status = 0
                # save draft
                # unlike normal messages, drafts have multiple receivers
                # because they haven't been split yet
                draft = save_draft(
                    current_user_mail,
                    user_input,
                    message,
                    time,
                    None,
                )
                # TODO: change this to a "Draft saved" message
                return redirect('/')
            # check if the post request has the optional file part
            if 'image' in request.files:
                file = request.files['image']
                # if user does not select file, browser also
                # submit an empty part without filename
                # also checks if the file is an image
                # despite the validator having already done so
                if file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # files are saved in a unique folder per each user
                    file_path = os.path.join(
                        flask.current_app.config['UPLOAD_FOLDER'],
                        current_user_mail,
                        filename
                    )
                    # make sure the path fits in our db field of 1024 char
                    if len(file_path) > 1024:
                        form.file.errors.append("Filename too big.")
                        return render_template(
                            'error_template.html',
                            form=form
                        )
                    file.save(file_path)
            # go ahead and parse the message
            correctly_sent, not_correctly_sent = send_messages(
                to_parse,
                current_user_mail,
                time,
                message,
                file_path
            )
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
    drafts = Message().query.filter_by(sender_email=current_user.email,
                                       status=0).all()
    return render_template('list/draft_list.html', drafts=drafts)


@send.route("/send/replay/<_id>", methods=["GET", "POST"])
@login_required
def replay(_id):
    if _id is None:
        return redirect('/inbox')
    message = None
    try:
        user_mail = current_user.get_email()
        message = Message().query.filter_by(
            id=int(_id),
            receiver_email=user_mail
        ).one()
    except NoResultFound:
        abort(403)
    user_input = message.sender_email
    form = ReplayForm()

    # correctly_sent = []
    # not_correctly_sent = []
    if request.method == 'POST':
        if form.validate_on_submit():
            message = form.data['message']
            time = form.data['time']
            to_parse = user_input.split(', ')
            current_user_mail = getattr(current_user, 'email')
            if request.form.get("save_button"):
                # the user asked to save this message
                save_draft(current_user_mail, user_input, message, time, None)
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
