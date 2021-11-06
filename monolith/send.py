import os
import sys
from pathlib import Path

from slugify import slugify
from werkzeug.utils import secure_filename

from monolith.background import deliver_message
from monolith.database import db, User, Message
import pytz

from monolith.blacklist import is_blacklisted
from monolith.views.content_filter import check_content_filter

if 'pytest' in sys.modules:
    UPLOAD_FOLDER = './monolith/static/images/test_uploads/'
else:
    UPLOAD_FOLDER = './monolith/static/images/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_messages(to_parse, current_user_mail, time, message, file):
    correctly_sent = []
    not_correctly_sent = []
    image = None
    # find users in database
    # if user found, enqueue, otherwise print error
    # TODO: generalize this based on the user, somehow
    #  maybe include timezone info in database?
    time_aware = pytz.timezone('Europe/Rome').localize(time)
    for address in to_parse:
        address = address.strip()
        exists = db.session.query(User.id). \
            filter_by(email=address).first() is not None
        if exists and not address == current_user_mail:
            # check if the receiver has this sender blacklisted

            if not is_blacklisted(sender=current_user_mail, receiver=address) \
                    and check_content_filter(address, message):
                # if we were handed a file but haven't saved it yet
                if file is not None and image is None:
                    image = save_picture(file, current_user_mail)

                # create a message entry in the database with status = pending
                unsent_message = Message()
                unsent_message.add_message(
                    message,
                    current_user_mail,
                    address,
                    time,
                    image,
                    1
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
            if address == current_user_mail:
                address = address + " (You)"
            not_correctly_sent.append(address)
    return correctly_sent, not_correctly_sent


def save_draft(current_user_mail, recipients, msg, time, image):
    new_draft = Message()
    # TODO: Maybe implement defaults for missing fields
    new_draft.add_message(msg, current_user_mail, recipients, time, image, 0)
    db.session.add(new_draft)
    db.session.commit()


def save_picture(file, current_user_mail):
    if file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # files are saved in a unique folder per each user
        folder_path = os.path.join(
            UPLOAD_FOLDER,
            slugify(current_user_mail),
        )
        file_path = os.path.join(folder_path, filename)
        # creating a webserver-approved file path
        path_to_save = \
            UPLOAD_FOLDER.split('/', 3)[-1] + \
            slugify(current_user_mail) + \
            '/' + filename
        # make sure the path fits in our db field of 1024 char
        if len(file_path) > 1024:
            raise FileExistsError("Filename too long.")
        if os.path.exists(file_path):
            raise NameError("Duplicate filename.")
        if not os.path.exists(folder_path):
            Path(folder_path).mkdir(parents=True, exist_ok=True)
        file.save(file_path)
        return path_to_save
    return None
