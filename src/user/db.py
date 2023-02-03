from enum import Enum, unique
from os import getenv

import aiomysql


@unique
class DbName(str, Enum):
    USER = "user"
    FEED = "feed"
    # POST = "user"  # in a production environment these would be separate databases


db_pools: dict[DbName, aiomysql.Pool] = {}


async def get_db(db_name: DbName) -> tuple[aiomysql.Connection, aiomysql.Pool] | None:
    if db := db_pools.get(db_name):
        return await db.acquire(), db
    raise Exception(f"Invalid database {db_name}")


async def select_one(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)
    if not cxn or not pool:
        raise Exception("Error getting database")

    curr = await cxn.cursor()
    await curr.execute(query, values)
    res = await curr.fetchone()

    pool.release(cxn)

    return res


async def select_all(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)

    curr = await cxn.cursor()
    await curr.execute(query, values)
    res = await curr.fetchall()

    pool.release(cxn)

    return res


async def insert_one(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)

    curr = await cxn.cursor()
    await curr.execute(query, values)

    pool.release(cxn)
    return True


async def delete_one(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)

    curr = await cxn.cursor()
    await curr.execute(query, values)

    pool.release(cxn)
    return True


async def update(db_name: DbName, query: str, values: tuple):
    cxn, pool = await get_db(db_name)

    curr = await cxn.cursor()
    await curr.execute(query, values)

    pool.release(cxn)
    return True


async def create_pool(db_name: DbName):
    db_pools[db_name] = await aiomysql.create_pool(
        host=getenv("DB_HOST"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        db=db_name.value,
        port=3306,
        autocommit=True,
    )
