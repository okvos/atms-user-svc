from .auth import routes as auth_routes
from .feed import routes as feed_routes
from .user import routes as user_routes

routes = [user_routes, auth_routes, feed_routes]
