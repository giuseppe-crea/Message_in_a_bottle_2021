from datetime import datetime

from flask import Blueprint, render_template, request, redirect, abort
from flask_login import login_required
from sqlalchemy.exc import NoResultFound

from monolith.auth import current_user
from monolith.database import Message
from monolith.forms import SendForm
from monolith.send import send_messages, save_draft
from monolith.views.doc import auto

send = Blueprint('send', __name__)


# noinspection PyUnusedLocal,PyUnboundLocalVariable
@send.route('/send', methods=['POST', 'GET'], defaults={'_id': None})
@send.route('/send/<_id>', methods=['POST', 'GET'])
@auto.doc(groups=['routes'])
@login_required
def _send(_id, data=""):
    """
    Endpoint for saving drafts and sending messages
    Takes values from the related form and either saves them as draft
    or passes the values on to the controller which will then proceed to queue
    the message with celery

    :param _id: the draft id
    :param data: a default parameter used for recipient setting
    :returns: a rendered view
    """
    form = SendForm()
    # if we are loading a draft:
    # the method check is required to avoid resetting the data on a POST
    if _id is not None and request.method == 'GET':
        # load it after checking its existence, and its status as a draft
        # drafts don't save images to save on server data usage
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
            file = None
            # grab must-have data which we are guaranteed to have
            message, user_input = form.data['message'], form.data['recipient']
            time = form.data['time']
            to_parse = user_input.split(', ')
            # we are saving a draft
            if request.form.get("save_button"):
                # save draft
                # unlike normal messages, drafts have multiple receivers
                # because they haven't been split yet
                draft = save_draft(
                    current_user_mail,
                    user_input,
                    message,
                    time
                )
                return redirect('/')
            # check if the post request has the optional file part
            if 'file' in request.files:
                file = request.files['file']
            # go ahead and deliver the messages
            try:
                correctly_sent, not_correctly_sent = send_messages(
                    to_parse,
                    current_user_mail,
                    time,
                    message,
                    file
                )
            except (FileExistsError, NameError) as e:
                form.file.errors.append(str(e))
                # noinspection PyUnresolvedReferences
                return render_template('error_template.html', form=form)
        else:
            # noinspection PyUnresolvedReferences
            return render_template('error_template.html', form=form)
        # noinspection PyUnresolvedReferences
        return render_template(
            'done_sending.html',
            users1=correctly_sent,
            users2=not_correctly_sent,
            text=message
        )
    else:
        # noinspection PyUnresolvedReferences
        return render_template('send.html', form=form)


@send.route('/send_draft_list', methods=['GET'])
@auto.doc(groups=['routes'])
@login_required
def get_message():
    """
    View of all drafts for a given user

    :returns: a rendered view
    """
    drafts = Message().query.filter_by(sender_email=current_user.email,
                                       status=0).all()
    # noinspection PyUnresolvedReferences
    return render_template('list/draft_list.html', drafts=drafts)
