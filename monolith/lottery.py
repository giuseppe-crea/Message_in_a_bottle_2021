import random

from monolith.database import LotteryPoints, db, User

price = 100
period = 259200
# difficulty = 4
prize = 100


def get_usr_points(user):
    user = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == user.get_id()).first()
    if user is None:
        return 0
    return user.points


class Lottery:
    def __init__(self):
        # self.difficulty = difficulty
        self.period = period
        self.prize = prize

    def start(self):
        pass

    def execute(self):
        users = [u.id for u in db.session.query(User).all()]
        winner_id = random.choice(users)
        winner = db.session.query(LotteryPoints).filter(
            LotteryPoints.id == winner_id).first()
        if winner is None:
            winner = LotteryPoints()
            winner.add_new_user(winner_id, prize)
            db.session.add(winner)
            db.session.commit()
        else:
            winner.points += self.prize
            db.session.commit()
        # TODO send a notification
        self._iter()

    def _iter(self):
        pass


def unlock_message(user):
    return None
