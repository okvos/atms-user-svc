import asyncio
from asyncio import run
from os import getenv

import aiohttp_cors
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from dotenv import load_dotenv

from src.common.upload_s3 import init_s3
from src.user.db import DbName, create_pool
from src.user.handlers import routes as app_routes
from src.user.middleware import middlewares

load_dotenv()


async def init():
    await create_pool(DbName.USER)
    await create_pool(DbName.FEED)

    init_s3()

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


if __name__ == "__main__":
    run(init())
