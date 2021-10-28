from datetime import datetime
import re
from html import escape
from math import floor
from monolith.background import deliver_message
from database import db, User


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def send_messages(to_parse, current_user_mail, time, message):
    real_recipients = []
    correctly_sent = []
    not_correctly_sent = []
    for address in to_parse:
        address = address.strip()
        if check(address):
            real_recipients.append(escape(address))
    # find users in database
    # if user found, enqueue, otherwise print error
    for address in real_recipients:
        exists = db.session.query(User.id). \
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
    return correctly_sent, not_correctly_sent
