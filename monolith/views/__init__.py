from .auth import auth
from .home import home
from .users import users
from .unreg import unreg

blueprints = [home, auth, users, unreg]
