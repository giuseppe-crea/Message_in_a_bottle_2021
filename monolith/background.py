from datetime import datetime

from celery import Celery

from monolith.database import User, db, UnsentMessage

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


def reload_unsent():
    query = db.session.query(UnsentMessage)
    rows = query.statement.execute().fetchall()
    for r in rows:
        deliver_message.apply_async((r.id, r.message, r.sender_email, r.receiver_email),
                                    eta=datetime.strptime(r.time, "%m/%d/%Y, %H:%M:%S"))


@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        # procedure to load all long-term stored messages yet to be delivered to recover from crashes
        # TODO: bring the broker online and uncomment this
        # reload_unsent()
    else:
        app = _APP

    return []


@celery.task
def deliver_message(_id, message, sender, receiver):
    # TODO: RPC to the module that will add the message in the receiver's list of messages
    # TODO: RPC that notifies the receiver
    # remove the message from the "to be delivered" database
    query = db.session.query(UnsentMessage).filter(UnsentMessage.id == _id)
    query.delete(synchronize_session=False)
    db.session.commit()
    return
