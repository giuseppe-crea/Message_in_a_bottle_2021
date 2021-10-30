from monolith.background import deliver_message
from monolith.database import db, User, Draft
import pytz

from monolith.views.blacklist import is_blacklisted


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
            # check if the receiver has this sender blacklisted
            if not is_blacklisted(sender=current_user_mail, receiver=address):
                # enqueue message with celery
                deliver_message.apply_async(
                    (None, message, current_user_mail, address, time),
                    eta=time_aware
                )
            # the sender will believe this message was correctly sent
            # but no actual message task will be dispatched
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
