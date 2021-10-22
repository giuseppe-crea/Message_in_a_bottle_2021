import re

from flask import Blueprint, render_template, request, escape, abort

from monolith.database import User, db
from monolith.forms import SendForm
from monolith.auth import current_user

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
def _send():
    form = SendForm()
    correctly_sent = []
    not_correctly_sent = []
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST':
            real_recipients = []
            if form.validate_on_submit():
                message, user_input = form.data['message'], form.data['recipient']
                message = escape(message)
                to_parse = user_input.split(', ')
                for address in to_parse:
                    address = address.strip()
                    if check(address):
                        real_recipients.append(escape(address))
                # find users in database
                # if user found, enqueue, otherwise print error
                for address in real_recipients:
                    exists = db.session.query(User.id).filter_by(email=address).first() is not None
                    if exists:
                        # queue message
                        print("OK! Sent " + message + " to " + address)
                        correctly_sent.append(address)
                    else:
                        print('KO! Address ' + address + " doesn't exist!")
                        not_correctly_sent.append(address)
            return render_template('done_sending.html', users1=correctly_sent, users2=not_correctly_sent)
        else:
            return render_template('send.html', form=form)
    else:
        abort(401)
