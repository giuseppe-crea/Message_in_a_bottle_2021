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
    """
    Checks the Allowed_Extensions constant to make sure we are sending an image
    :param filename: the file's name, extension included
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_messages(to_parse, current_user_mail, time, message, file):
    """
    Enqueues a message with celery performing checks on the sender/receiver
    Saves any file it gets to a folder specific to that sender
    :param to_parse: list of mail recipient addresses, comma separated
    :param current_user_mail: mail of sender
    :param time: time of delivery, cannot be in the past
    :param message: the actual message, max size of 1024 char
    :param file: a file to save, images only, can be None
    :return correctly_sent: list of mail addresses to which the message was
    correctly sent, including messages which blacklist the sender
    :return not_correctly_sent: list of mail addresses which were not real
    users or were the sender themselves
    """
    correctly_sent = []
    not_correctly_sent = []
    image = None
    # find users in database
    # if user found, enqueue, otherwise print error
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


def save_draft(current_user_mail, recipients, msg, time):
    """
    saves a message with status of draft
    :param current_user_mail: mail of sender
    :param time: time of delivery, cannot be in the past
    :param recipients: string containing the unparsed list of recipients
    :param msg: the actual message, max size of 1024 char
    """
    new_draft = Message()
    new_draft.add_message(msg, current_user_mail, recipients, time, None, 0)
    db.session.add(new_draft)
    db.session.commit()


def save_picture(file, current_user_mail):
    """
    Saves a picture on the server
    This method is only called for message that must be sent, and not drafts
    This method creates a new folder with the user's mail if none exists
    to allow different users to send files with the same filename
    :param file: the file to save
    :param current_user_mail: the mail of the current user
    :return path_to_save: the path from which the image can be displayed
    """
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
