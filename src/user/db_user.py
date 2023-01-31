from asyncio import get_running_loop

from attr import define
from bcrypt import checkpw, gensalt, hashpw

from src.user.db import DbName, select_one


@define
class AccountNotFound(Exception):
    error: str


@define
class Account:
    user_id: int
    username: str
    password: str
    email_address: str


async def encrypt_password(password: str) -> str:
    return (
        await get_running_loop().run_in_executor(
            None, hashpw, password.encode("utf-8"), gensalt()
        )
    ).decode("utf-8")


async def check_password(password: str, hashed_password: str) -> bool:
    return await get_running_loop().run_in_executor(
        None, checkpw, password.encode("utf-8"), hashed_password.encode("utf-8")
    )


async def get_account_by_id(user_id: int) -> Account:
    user = await select_one(
        DbName.USER,
        "select `user_id`, `username`, `password`, `email_address` from account where user_id = %s",
        (user_id,),
    )
    if not user:
        raise AccountNotFound(f"Id: {user_id} not found")
    return Account(*user)


async def get_account_by_username(username: str) -> Account:
    user = await select_one(
        DbName.USER,
        "select `user_id`, `username`, `password`, `email_address` from account where username = %s",
        (username,),
    )
    if not user:
        raise AccountNotFound(f"Username: {username} not found")
    return Account(*user)
