from monolith.database import Message


def filter_or(message, keywards):
    s = message.sender_email
    r = message.receiver_email
    c = message.message
    for k in keywards:
        if s.find(k) or r.find(k) or c.find(k):
            return True
    return False


def filter_and(message, keywards):
    s = message.sender_email
    r = message.receiver_email
    c = message.message
    for k in keywards:
        if not (s.find(k) or r.find(k) or c.find(k)):
            return False
    return True


def search_keywords(user, keywords, inbox=True, all=False):
    if inbox:
        messages = Message().query.filter_by(
            Message.receiver_email == user.get_email(),
            Message.visible_to_receiver is True).all()
    else:
        messages = Message().query.filter_by(
            Message.sender_email == user.get_email(),
            Message.visible_to_sender is True).all()
    if all:
        return [m for m in messages if filter_and(m, keywords)]
    return [m for m in messages if filter_or(m, keywords)]
