import os

from monolith.database import db, Message


# this method assumes values have been previously checked and are safe
def delete_for_receiver(message_query: Message):
    message_query.visible_to_receiver = False
    if not message_query.visible_to_sender:
        delete_picture(message_query)
        db.session.delete(message_query)
    db.session.commit()


def delete_for_sender(message_query: Message):
    message_query.visible_to_sender = False
    if not message_query.visible_to_receiver:
        delete_picture(message_query)
        db.session.delete(message_query)
    db.session.commit()


def delete_picture(message_query):
    if message_query.image is not None and message_query.image != '':
        file_path = os.path.join('./monolith/static', message_query.image)
        if os.path.exists(file_path):
            os.remove(file_path)
