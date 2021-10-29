from .auth import auth
from .home import home
from .users import users
from .unreg import unreg
from .send import send
from .list import list_blueprint

blueprints = [home, auth, users, send, unreg, list_blueprint]
