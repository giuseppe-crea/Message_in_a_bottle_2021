from .auth import auth
from .home import home
from .inbox import inbox
from .users import users
from .unreg import unreg
from .send import send
from .outbox import outbox

blueprints = [home, auth, users, send, unreg, outbox, inbox]
