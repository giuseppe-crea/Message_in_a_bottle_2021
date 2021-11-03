import random
from threading import Timer

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


def give_points(winner_id, points):
    winner = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == winner_id).first()

    if winner is None:
        winner = LotteryPoints()
        winner.add_new_user(winner_id, points)
        db.session.add(winner)
        db.session.commit()
    else:
        winner.points += points
        db.session.commit()

def set_points(winner_id, points):
    winner = db.session.query(LotteryPoints).filter(
        LotteryPoints.id == winner_id).first()

    if winner is None:
        winner = LotteryPoints()
        winner.add_new_user(winner_id, points)
        db.session.add(winner)
        db.session.commit()
    else:
        winner.points = points
        db.session.commit()


class Lottery:
    def __init__(self, app):
        # self.difficulty = difficulty
        self.app = app
        self.period = float(period)
        self.prize = prize
        self.cancelled = False
        self.error = None
        self.timer = None

    def start(self):
        self._iter()

    def execute(self):
        if self.cancelled:
            return
        try:
            with self.app:
                users = [u.id for u in db.session.query(User).all()]
                winner_id = random.choice(users)
                give_points(winner_id, self.prize)
                # TODO send a notification
                #self.cancelled = True
                #self._iter()
        except Exception as e:
            self.cancelled = True
            self.error = e

    def _iter(self):
        if self.cancelled:
            return
        try:
            self.timer = Timer(self.period, self.execute)
            self.timer.start()
        except Exception as e:
            self.cancelled = True
            self.error = e

    def cancel(self):
        self.cancelled = True


def unlock_message(user):
    return -1, 0
