import html
import re
from datetime import datetime
from math import floor

from flask import Blueprint, render_template, request, escape, redirect, url_for
from flask_login import login_required

from monolith.database import User, Draft, db
from monolith.forms import SendForm, RecipientsListForm
from monolith.auth import current_user
from monolith.background import deliver_message

send = Blueprint('send', __name__)


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False

def save_draft(form):
    msg, recipients, time = html.escape(form.data['message']), form.data['recipient'], form.data['time']
    new_draft = Draft()
    new_draft.add_new_draft(current_user.email, recipients, msg, time)

    db.session.add(new_draft)
    db.session.commit()


@send.route('/send', methods=['POST', 'GET'])
@login_required
# data is a default parameter used for recipient setting
def _send(data=""):
    form = SendForm()
    correctly_sent = []
    not_correctly_sent = []
    if request.method == 'POST':
        real_recipients = []
        if form.validate_on_submit():
            message, user_input = html.escape(form.data['message']), form.data['recipient']
            time = form.data['time']
            is_draft = form.data['is_draft']
            to_parse = user_input.split(', ')
            
            if is_draft == True:
                save_draft(form)
                return redirect('/')


            for address in to_parse:
                address = address.strip()
                if check(address):
                    real_recipients.append(escape(address))
            # find users in database
            # if user found, enqueue, otherwise print error
            current_user_mail = getattr(current_user, 'email')
            for address in real_recipients:
                exists = db.session.query(User.id).filter_by(email=address).first() is not None
                if exists and not address == current_user_mail:
                    # enqueue message with celery
                    # TODO: find out what the proper format for ETA is and replace delay
                    first_time = datetime.now()
                    difference = time - first_time
                    timedelta_seconds = floor(difference.total_seconds())
                    
                    deliver_message.apply_async((message, current_user_mail, address), countdown=timedelta_seconds)
                    correctly_sent.append(address)
                else:
                    not_correctly_sent.append(address)
            if len(correctly_sent) > 0:
                db.session.commit()
        else:
            return render_template('error_template.html', form=form)
        return render_template('done_sending.html', users1=correctly_sent, users2=not_correctly_sent,
                               text=html.unescape(message))
    else:
        return render_template('send.html', form=form)


@send.route('/send/<id>', methods=['GET'])
def retrieve_one_msg(id):
    form = SendForm()
    print(id)
    draft = Draft().query.filter_by(id = int(id), sender_email=current_user.email).one()
    form.message.data = draft.message
    form.recipient.data = draft.recipients
    
    return render_template('send.html', form=form)

@send.route('/send_draft_list', methods=['GET'])
def get_message():
   drafts = Draft().query.filter_by(sender_email=current_user.email).all()
   return render_template('draft/draft_list.html', drafts = drafts)

@send.route('/list_of_recipients', methods=['POST', 'GET'])
def _display_users():

    # instantiate the form
    form = RecipientsListForm()

    # ordering alphabetically and filtering admin accounts
    _users = db.session.query(User).filter(User.firstname != 'Admin').order_by(User.lastname)

    # sets choices
    form.radio_form.choices = [(user.email, \
                                user.lastname + ' ' + user.firstname + ': ' + user.email) for user in _users]

    if request.method == 'POST':  # POST request

        if len(request.form) != 0:  # check the selection of a radio button
            selected_recipient = request.form['radio_form']
            return redirect(url_for('send._send', data=selected_recipient))  # redirecting to /send

        else:  # no recipient selected
            return redirect(url_for('send._send'))

    else:  # GET request, returns the list_of_recipients.html page
        return render_template('list_of_recipients.html', form=form)
