from enum import Enum, unique
from os import getenv

import aiomysql


@unique
class DbName(str, Enum):
    USER = "user"


db_pools: dict[DbName, aiomysql.Pool] = {}


async def get_db(db_name: DbName) -> tuple[aiomysql.Connection, aiomysql.Pool] | None:
    if db := db_pools.get(db_name):
        return await db.acquire(), db
    return None


async def select_one(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)

    curr = await cxn.cursor()
    await curr.execute(query, values)
    res = await curr.fetchone()

    pool.release(cxn)

    return res


async def create_pool(db_name: DbName):
    db_pools[db_name] = await aiomysql.create_pool(
        host=getenv("DB_HOST"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        db=db_name.value,
        port=3306,
        autocommit=True,
    )
