import html
import re
from datetime import datetime
from math import floor

from flask import Blueprint, render_template, request, escape
from flask_login import login_required

from monolith.database import User, db
from monolith.forms import SendForm
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


# noinspection PyUnusedLocal,PyUnresolvedReferences
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
                exists = db.session.query(User.id).\
                             filter_by(email=address).first() is not None
                if exists and not address == current_user_mail:
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

