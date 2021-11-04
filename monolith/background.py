import os
import pathlib
from datetime import datetime

from celery import Celery
from sqlalchemy import and_
from sqlalchemy.exc import NoResultFound

from monolith import lottery
from monolith.database import db, Message, Notification

if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis:6379/0'
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None
UPLOAD_FOLDER = None


@celery.task
def do_task(app):
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

    sender.add_periodic_task(
        float(lottery.period),
        lottery_task.s(_APP),
        name='lottery task'
    )


# task to periodically send unsent messages past due
@celery.task
def send_unsent_past_due(app):
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        query = db.session.query(Message).filter(and_(
            Message.status == 1,
            Message.time <= datetime.now().strftime('%Y-%m-%dT%H:%M'))
        )
        for row in query:
            row.status = 2
        db.session.commit()


# task to delete pictures with no reference in the database
# to be run periodically
@celery.task
def cleanup_pictures(app):
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
    # TODO: RPC that notifies the receiver
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        # find the message with that given id
        try:
            message = Message().query.filter_by(id=int(message_id)).one()
            message.status = 2
            # notify recipient
            notification = Notification()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            title = message.sender_email + " Sent You a Message"
            description = \
                "Check Your <a href=\"/inbox\">Inbox</a> to <a href=\"/inbox/"\
                + str(message_id) + "\">Open It</a>"
            notification.add_notification(
                message.receiver_email,
                title,
                description,
                timestamp,
                False
            )
            db.session.add(notification)
            db.session.commit()
        except NoResultFound:
            quit(0)  # this means the message was retracted
    return "Done"


@celery.task
def lottery_task(app):
    global _APP
    do_task(app)
    # noinspection PyUnresolvedReferences
    with _APP.app_context():
        lottery.execute()
