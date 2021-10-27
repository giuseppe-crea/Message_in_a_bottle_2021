from .auth import auth
from .home import home
from .users import users
from .unreg import unreg
from .send import send
from .receive import receive

blueprints = [home, auth, users, send, unreg, receive]