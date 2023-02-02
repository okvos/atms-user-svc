import asyncio
from asyncio import run
from os import getenv

import aiohttp_cors
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from dotenv import load_dotenv

from src.user.db import DbName, create_pool
from src.user.db_user import get_account_by_id
from src.user.handlers import routes as app_routes
from src.user.middleware import middlewares

load_dotenv()


async def init():
    await create_pool(DbName.USER)
    await create_pool(DbName.FEED)

    cookie_name = "atms_session_id"

    app = web.Application(middlewares=middlewares)
    setup(
        app,
        EncryptedCookieStorage(
            cookie_name=cookie_name,
            secret_key=getenv("COOKIE_KEY"),
            domain=".atmospheretest.site",
        ),
    )
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    for route in app_routes:
        app.add_routes(route)

    for route in list(app.router.routes()):
        cors.add(route)

    await asyncio.gather(web._run_app(app))


async def handle(request):
    name = request.match_info.get("name", "Anonymous")
    text = "Hello, " + name
    print("Go")
    print(await get_account_by_id(1))
    return web.Response(text=text)


if __name__ == "__main__":
    run(init())
