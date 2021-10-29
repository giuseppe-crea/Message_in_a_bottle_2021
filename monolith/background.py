from celery import Celery, shared_task
from monolith.database import db, SentMessage
import os

if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis:6379/0'
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        _APP = create_app()
        db.init_app(_APP)
    return []


@celery.task
def deliver_message(app, message, sender, receiver, time):
    # TODO: RPC that notifies the receiver
    global _APP
    if app is None:
        do_task()
        app = _APP
    # noinspection PyUnresolvedReferences
    with app.app_context():
        # create an entry in the sent table
        unsent_message = SentMessage()
        unsent_message.add_message(message, sender, receiver, time)
        db.session.add(unsent_message)
        db.session.commit()
    return "Done"
