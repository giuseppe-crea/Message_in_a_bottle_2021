import re
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from monolith.database import Draft, User, db
from monolith.forms import SendForm, RecipientsListForm
from monolith.auth import current_user
from monolith.send import send_messages, save_draft

send = Blueprint('send', __name__)


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False


# noinspection PyUnusedLocal
@send.route('/send', methods=['POST', 'GET'], defaults={'_id': None})
@send.route('/send/<_id>', methods=['POST', 'GET'])
@login_required
# data is a default parameter used for recipient setting
def _send(_id, data=""):
    form = SendForm()
    if _id is not None and request.method == 'GET':
        # we are viewing a draft, load it
        draft = Draft().query.filter_by(
            id=int(_id),
            sender_email=current_user.email
        ).one()
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


@send.route('/list_of_recipients', methods=['POST', 'GET'])
def _display_users():
    # instantiate the form
    form = RecipientsListForm()
    # ordering alphabetically, filtering admin accounts and the sender itself
    _users = db.session.query(User).order_by(User.lastname).\
        filter(User.firstname != 'Admin').all()
    # sets choices
    form.multiple_field_form.choices = \
        [(user.email, user.lastname + ' ' + user.firstname + ': ' + user.email)
         for user in _users]
    if request.method == 'POST':  # POST request
        if len(request.form) != 0:  # check the selection of a recipient
            # create a list of emails, removing the submitted label
            selected_recipient_list = \
                request.form.getlist('multiple_field_form')
            # create a dictionary to construct the right structure
            payload = {'email_list': ', '.join(selected_recipient_list)}
            # send a list of comma-separated emails
            # redirecting to /send
            return redirect(url_for('send._send', data=payload['email_list']))
        else:  # no recipient selected
            return redirect(url_for('send._send'))
    else:  # GET request, returns the list_of_recipients.html page
        return render_template('list_of_recipients.html', form=form)
