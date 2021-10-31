from celery import Celery
from monolith.database import db, Message
from sqlalchemy.exc import NoResultFound
import os

if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis:6379/0'
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.task
def do_task(app):
    global _APP
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
    return app


# TODO: task to periodically send unsent messages past due


# TODO: task to delete pictures with no reference in the database


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
            db.session.commit()
        except NoResultFound:
            quit(0)  # this means the message was retracted
    return "Done"
