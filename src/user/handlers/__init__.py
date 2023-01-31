from .auth import routes as auth_routes
from .user import routes as user_routes

routes = [user_routes, auth_routes]
