import datetime
import html
import re

from flask import Blueprint, render_template, request, escape, abort

from monolith.database import User, db, UnsentMessage
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


@send.route('/send', methods=['POST', 'GET'])
def _send():
    form = SendForm()
    correctly_sent = []
    not_correctly_sent = []
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST':
            real_recipients = []
            if form.validate_on_submit():
                message, user_input = html.escape(form.data['message']), form.data['recipient']
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
                    exists = db.session.query(User.id).filter_by(email=address).first() is not None
                    if exists and not address == current_user_mail:
                        # save message, sender, receiver, date to the database of unsent messages
                        unsent_message = UnsentMessage()
                        unsent_message.add_message(message, current_user_mail, address,
                                                   time.strftime("%m/%d/%Y, %H:%M:%S"))
                        db.session.add(unsent_message)
                        # enqueue message with celery
                        # TODO: bring the broker online and uncomment this
                        # deliver_message.apply_async((unsent_message.get_id(), message, current_user_mail, address),
                        #                            eta=time)
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
    else:
        abort(401)
