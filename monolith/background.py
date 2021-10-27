from celery import Celery
from monolith.database import db, SentMessage

BACKEND = BROKER = 'redis://localhost:6379'
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
def deliver_message(message, sender, receiver, time):
    # TODO: RPC that notifies the receiver
    global _APP
    do_task()
    with _APP.app_context():
        # create an entry in the sent table
        unsent_message = SentMessage()
        unsent_message.add_message(message, sender, receiver, time)
        db.session.add(unsent_message)
        db.session.commit()
        # placeholder delivery
        print("Your message is \"" + message + "\"\nTo be delivered to: " +
              receiver + "\nSent from: " + sender)
    return "Done"
