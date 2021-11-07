import os
import pathlib
import random
from datetime import datetime

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound

from monolith import lottery
from monolith.database import db, Message, Notification, User

# Check a specifically set environment variable for the address of the backend
# said address could also be obtained from an env variable
# but this is not currently required
if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis:6379/0'
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None
UPLOAD_FOLDER = None


@celery.task
def do_task(app):
    """
    instantiate an app if none is present

    :param app: the flask.current_app object, can be None
    """
    global _APP
    global UPLOAD_FOLDER
    # lazy init
    if app is None:
        if _APP is None:
            from monolith.app import create_app
            _APP = create_app()
            db.init_app(_APP)
        app = _APP
    elif _APP is None:
        db.init_app(app)
        _APP = app
    UPLOAD_FOLDER = app.config['UPLOADED_IMAGES_DEST']
    return app


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    celery beat support function
    """
    # Checks for unsent and overdue messages every 5 minutes
    sender.add_periodic_task(
        300.0,
        send_unsent_past_due.s(_APP),
        name='crash recovery'
    )
    # Every hour, tries to clean up old pics
    sender.add_periodic_task(
        3600.0,
        cleanup_pictures.s(_APP),
        name='expired images cleanup'
    )
    # Runs the lottery every lottery period
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_month=1),
        lottery_task.s(_APP),
        name='lottery task'
    )


@celery.task
def send_unsent_past_due(app):
    """
    task to periodically send unsent messages past due
    useful in case of catastrophic failure of celery

    :param app: the flask.current_app object, can be None
    """
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        query = db.session.query(Message).filter(and_(
            Message.status == 1,
            Message.time <= datetime.now().strftime('%Y-%m-%dT%H:%M'))
        )
        for row in query:
            deliver_message(app, row.get_id())


@celery.task
def cleanup_pictures(app):
    """
    task to delete pictures with no reference in the database
    this is one possible way to account for forwards and deletions

    :param app: the flask.current_app object, can be None
    """
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        # noinspection PyTypeChecker
        for path, sub_dirs, files in os.walk(UPLOAD_FOLDER):
            for name in files:
                full_path = pathlib.PurePath(path, name)
                if os.path.isfile(full_path):
                    # build the string saved within the messages
                    path_to_save = str(full_path).split('static')[1]
                    path_to_save = path_to_save[1:]
                    # necessary when testing under windows
                    path_to_save = path_to_save.replace("\\", "/")
                    if Message.query.filter(
                            (Message.image == path_to_save)).first() is None:
                        os.remove(full_path)


# noinspection PyUnresolvedReferences
@celery.task
def deliver_message(app, message_id):
    """
    Task to deliver a message by editing its status in the database

    :param app: the flask.current_app object, can be None
    :param message_id: the id of the message to deliver in the database
    """
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        # find the message with that given id
        try:
            message = Message().query.filter_by(id=int(message_id)).one()
            message.status = 2
            # notify recipient
            timestamp = message.time
            title = message.sender_email + " Sent You a Message"
            description = \
                "Check Your <a href=\"/inbox\">Inbox</a> to <a href=\"/inbox/"\
                + str(message.get_id()) + "\">Open It</a>"
            create_notification(
                title,
                description,
                timestamp,
                message.receiver_email
            )
            db.session.commit()
        except NoResultFound:
            pass  # this means the message was retracted
    return "Done"


@celery.task
def lottery_task(app):
    """
    Runs the lottery

    :param app: the flask.current_app object, can be None
    """
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        users = User.query.all()
        winner = random.choice(users)
        if winner is not None:
            winner.add_points(lottery.prize)
            db.session.commit()
            create_notification(
                "Lottery win",
                "You have won" + str(lottery.price) + "points",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                winner.email
            )


@celery.task
def create_notification(title, description, timestamp, target):
    """
    Creates a notification element in the database

    :param title: Notification title
    :param description: Notification body text
    :param timestamp: timestamp to display on the Notification
    :param target: the user mail address to which the notification is addressed
    """
    notification = Notification()
    notification.add_notification(
        target,
        title,
        description,
        timestamp,
        False
    )
    db.session.add(notification)
    db.session.commit()
