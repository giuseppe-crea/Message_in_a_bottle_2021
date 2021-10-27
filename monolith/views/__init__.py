from .blacklist import blacklist
from .auth import auth
from .home import home
from .users import users
from .unreg import unreg
from .send import send

blueprints = [home, auth, users, send, unreg, blacklist]
