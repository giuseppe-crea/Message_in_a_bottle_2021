from .auth import auth
from .home import home
from .box import box
from .users import users
from .unreg import unreg
from .send import send
from .list import list_blueprint
from .blacklist import blacklist
from .report import report
from .content_filter import content_filter
from .alerts import alerts
from .credentials import credentials
from .calendar import calendar
from .doc import doc


blueprints = [
  home,
  auth,
  users,
  send,
  unreg,
  box,
  list_blueprint,
  blacklist,
  report,
  alerts,
  content_filter,
  credentials,
  calendar,
  doc
]
