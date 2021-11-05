import random
from datetime import datetime

from monolith.database import LotteryPoints, db, User, Notification

# global parameters of the lottery
price = 100
period = 2592000
prize = 100


def get_usr_points(user):
    """
    Get the user's lottery point from the database
    :param user: an User object
    :return: user's lottery points
    """
    user = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == user.get_id()).first()
    if user is None:
        return 0
    return user.points


def give_points(user_id, points):
    """
    Add new points to the user's account
    """
    winner = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == user_id).first()

    if winner is None:
        winner = LotteryPoints()
        winner.add_new_user(user_id, points)
        db.session.add(winner)
        db.session.commit()
    else:
        winner.points += points
        db.session.commit()


def set_points(user_id, points):
    """
    Set the total points of the user
    """
    winner = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == user_id).first()

    if winner is None:
        winner = LotteryPoints()
        winner.add_new_user(user_id, points)
        db.session.add(winner)
        db.session.commit()
    else:
        winner.points = points
        db.session.commit()


def execute():
    """
    Execute a lottery round
    """
    # get the list of all users id
    users = db.session.query(User).all()
    # select a random id
    winner = random.choice(users)
    # add the prize to the winner's points
    give_points(winner.id, prize)
    _send_notification(winner.email)


def _send_notification(email):
    notification = Notification()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = "Lottery win"
    description = "You have won" + str(prize) + "points"
    notification.add_notification(
        email,
        title,
        description,
        timestamp,
        False
    )
    db.session.add(notification)
    db.session.commit()
