import re
from monolith.background import deliver_message
from monolith.database import db, User, Draft
import pytz


def check(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def send_messages(to_parse, current_user_mail, time, message):
    correctly_sent = []
    not_correctly_sent = []
    # find users in database
    # if user found, enqueue, otherwise print error
    # TODO: generalize this based on the user, somehow
    time_aware = pytz.timezone('Europe/Rome').localize(time)
    for address in to_parse:
        address = address.strip()
        exists = db.session.query(User.id).\
            filter_by(email=address).first() is not None
        if exists and not address == current_user_mail:
            # enqueue message with celery
            deliver_message.apply_async(
                (None, message, current_user_mail, address, time),
                eta=time_aware
            )
            correctly_sent.append(address)
        else:
            not_correctly_sent.append(address)
    return correctly_sent, not_correctly_sent


def save_draft(current_user_mail, recipients, msg, time):
    new_draft = Draft()
    # TODO: Maybe implement defaults for missing fields
    new_draft.add_new_draft(current_user_mail, recipients, msg, time)
    db.session.add(new_draft)
    db.session.commit()
