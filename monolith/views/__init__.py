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
from .report import report
from .content_filter import content_filter

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
  blacklist,
  report,
  content_filter
]
