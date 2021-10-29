import html
import re
from datetime import datetime
from math import floor

from flask import Blueprint, render_template, request, escape, redirect, \
    url_for
from flask_login import login_required

from monolith.auth import current_user
from monolith.background import deliver_message
from monolith.database import User, db
from monolith.forms import SendForm, RecipientsListForm
from monolith.views.blacklist import _is_blacklisted

send = Blueprint('send', __name__)


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False


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
            message, user_input = \
                html.escape(form.data['message']), form.data['recipient']
            time = form.data['time']
            to_parse = user_input.split(', ')
            for address in to_parse:
                address = address.strip()
                if check(address):
                    real_recipients.append(escape(address))
            # find users in database
            # if user found, enqueue, otherwise print error
            current_user_mail = getattr(current_user, 'email')
            for address in real_recipients:
                exists = db.session.query(User.id). \
                             filter_by(email=address).first() is not None
                if exists and not address == current_user_mail \
                        and not _is_blacklisted(sender=current_user_mail,
                                                receiver=address):
                    # enqueue message with celery
                    # TODO: find out what the proper format for
                    #  ETA is and replace delay
                    first_time = datetime.now()
                    difference = time - first_time
                    timedelta_seconds = floor(difference.total_seconds())
                    deliver_message.apply_async(
                        (message, current_user_mail, address, time),
                        countdown=timedelta_seconds
                    )
                    correctly_sent.append(address)
                else:
                    not_correctly_sent.append(address)
            if len(correctly_sent) > 0:
                db.session.commit()
        else:
            return render_template('error_template.html', form=form)
        return render_template(
            'done_sending.html',
            users1=correctly_sent,
            users2=not_correctly_sent,
            text=html.unescape(message)
        )
    else:
        return render_template('send.html', form=form)


@send.route('/list_of_recipients', methods=['POST', 'GET'])
def _display_users():
    # instantiate the form
    form = RecipientsListForm()

    # ordering alphabetically, filtering admin accounts and the sender itself
    _users = db.session.query(User).order_by(User.lastname). \
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
            payload = {'email_list': ','.join(selected_recipient_list)}
            # send a list of comma-separated emails
            # redirecting to /send
            return redirect(url_for('send._send', data=payload['email_list']))

        else:  # no recipient selected
            return redirect(url_for('send._send'))

    else:  # GET request, returns the list_of_recipients.html page
        return render_template('list_of_recipients.html', form=form)
