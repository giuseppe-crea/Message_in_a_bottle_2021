from .auth import auth
from .home import home
from .inbox import inbox
from .users import users
from .unreg import unreg
from .send import send
from .outbox import outbox
from .admin import admin
from .list import list_blueprint
from .blacklist import blacklist

blueprints = [
  home,
  auth,
  users,
  send,
  unreg,
  outbox,
  inbox,
  admin,
  list_blueprint,
  blacklist
]
