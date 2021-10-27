import requests
from celery import Celery
from monolith.database import db
from celery.utils.log import get_task_logger

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)


logger = get_task_logger(__name__)

_APP = None

@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    return []


@celery.task
def deliver_message(message, sender, receiver):
    # TODO: RPC to the module that will add the message in the receiver's list of messages
    # TODO: RPC that notifies the receiver
    # placeholder delivery
    logger.info('Your message is {0} \nTo be delivered to: {1} \nSent from: {2}'
    .format(message, receiver, sender))
    _APP.post("/inbox")
    

    return "Done"
