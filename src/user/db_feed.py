from attr import define
from pymysql.err import IntegrityError

from src.user.db import DbName, delete_one, insert_one, select_all, select_one


@define
class PostNotFound(Exception):
    error: str


@define
class Post:
    post_id: int
    user_id: int
    date: int
    text: str
    is_liked: bool = False


@define
class PostLike:
    post_id: int
    user_id: int


POST_FETCH_LIMIT = 10


async def get_post_by_id(post_id: int) -> Post:
    post = await select_one(
        DbName.FEED,
        "select `post_id`, `user_id`, `date`, `text` from post where post_id = %s",
        (post_id,),
    )
    if not post:
        raise PostNotFound(f"Id: {post_id} not found")
    return Post(*post)


async def get_posts_by_user_id(user_id: int) -> list[Post]:
    posts = await select_all(
        DbName.FEED,
        "select `post_id`, `user_id`, `date`, `text` from post where user_id = %s limit %s",
        (user_id, POST_FETCH_LIMIT),
    )
    if not posts:
        raise PostNotFound(f"No posts found")
    return [Post(*post) for post in posts]


async def like_post(user_id: int, post_id: int) -> bool:
    try:
        await insert_one(
            DbName.FEED, "insert into post_like (user_id, post_id) values (%s, %s)", (user_id, post_id)
        )
    except IntegrityError:
        return False
    return True


async def unlike_post(user_id: int, post_id: int):
    await delete_one(
        DbName.FEED,
        "delete from post_like where user_id = %s and post_id = %s",
        (user_id, post_id),
    )


async def is_post_liked_by_user_id(post_id: int, user_id: int) -> bool:
    res = await select_one(
        DbName.FEED,
        "select 1 from post_like where post_id = %s and user_id = %s",
        (post_id, user_id),
    )
    return res is not None


async def are_posts_liked_by_user_id(post_ids: list[int], user_id: int) -> tuple[int]:
    post_ids_string = ",".join(["%s"] * len(post_ids))
    res = await select_one(
        DbName.FEED,
        f"select post_id from post_like where post_id in ({post_ids_string}) and user_id = %s",
        (*post_ids, user_id),
    )
    return res if res else ()
