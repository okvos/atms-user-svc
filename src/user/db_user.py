from asyncio import get_running_loop

from attr import define
from bcrypt import checkpw, gensalt, hashpw

from src.user.db import DbName, select_one, select_all


@define
class AccountNotFound(Exception):
    error: str


@define
class Account:
    user_id: int
    username: str
    password: str
    email_address: str


@define
class Profile:
    user_id: int
    username: str
    bio: str
    header_image_url: str


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


async def get_profile_by_username(username: str) -> Profile:
    profile = await select_one(
        DbName.USER,
        "select `user_id`, `username`, `bio`, `header_image_url` from profile where username = %s",
        (username,),
    )
    if not profile:
        raise AccountNotFound(f"Profile: {username} not found")
    return Profile(*profile)


async def get_profiles_by_user_ids(user_ids: set[int]) -> dict[int, Profile]:
    profile_list_str = ",".join(["%s"] * len(user_ids))
    profiles = await select_all(
        DbName.USER,
        f"select `user_id`, `username`, `bio`, `header_image_url` from profile where user_id in ({profile_list_str})",
        tuple(user_ids),
    )
    return {profile[0]: Profile(*profile) for profile in profiles}
