import random

from monolith.database import LotteryPoints, db, User

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
    users = [u.id for u in db.session.query(User).all()]
    # select a random id
    winner_id = random.choice(users)
    # add the prize to the winner's points
    give_points(winner_id, prize)
