# some checks for the add functionality
from monolith.database import Blacklist, db, User


def _check_exist(email):
    return db.session.query(User.query.filter(User.email == email)
                            .exists()).scalar()


def _check_already_blocked(user, email):
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == email,
            Blacklist.owner == user.get_id()).exists()).scalar()


def _check_itself(user, email):
    usr = db.session.query(User).filter(User.id == user.get_id()).first()
    return usr.email == email


def _check_add_blacklist(user, email):
    return _check_exist(email) and not (
            _check_already_blocked(user, email) or
            _check_itself(user, email))


def add2blacklist_local(user, email):
    if _check_add_blacklist(user, email):
        # insert the email to block in the user's blacklist
        blacklist = Blacklist()
        blacklist.add_blocked_user(user.get_id(), email)
        db.session.add(blacklist)
        db.session.commit()


def is_blacklisted(sender, receiver):
    receiver_id = db.session.query(User).filter(User.email == receiver) \
        .first().id
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == sender,
            Blacklist.owner == receiver_id).exists()).scalar()
