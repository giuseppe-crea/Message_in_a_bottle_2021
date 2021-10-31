from monolith.background import deliver_message
from monolith.database import db, User, Message
import pytz

from monolith.views.blacklist import is_blacklisted

UPLOAD_FOLDER = '/media/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_messages(to_parse, current_user_mail, time, message, image):
    correctly_sent = []
    not_correctly_sent = []
    # find users in database
    # if user found, enqueue, otherwise print error
    # TODO: generalize this based on the user, somehow
    #  maybe include timezone info in database?
    time_aware = pytz.timezone('Europe/Rome').localize(time)
    for address in to_parse:
        address = address.strip()
        exists = db.session.query(User.id).\
            filter_by(email=address).first() is not None
        if exists and not address == current_user_mail:
            # check if the receiver has this sender blacklisted
            if not is_blacklisted(sender=current_user_mail, receiver=address):
                # create a message entry in the database with status = pending
                status = '1'
                unsent_message = Message()
                unsent_message.add_message(
                    message,
                    current_user_mail,
                    address,
                    time,
                    image,
                    status
                )
                db.session.add(unsent_message)
                db.session.commit()
                # enqueue message with celery
                deliver_message.apply_async(
                    (None, unsent_message.get_id()),
                    eta=time_aware
                )
            # the sender will believe this message was correctly sent
            # but no actual message task will be dispatched
            correctly_sent.append(address)
        else:
            not_correctly_sent.append(address)
    return correctly_sent, not_correctly_sent


def save_draft(current_user_mail, recipients, msg, time, image):
    new_draft = Message()
    # TODO: Maybe implement defaults for missing fields
    new_draft.add_message(msg, current_user_mail, recipients, time, image, 0)
    db.session.add(new_draft)
    db.session.commit()
