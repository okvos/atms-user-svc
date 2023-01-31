from attr import define

from src.user.db import DbName, select_all, select_one


@define
class PostNotFound(Exception):
    error: str


@define
class Post:
    post_id: int
    user_id: int
    date: int
    text: str


POST_FETCH_LIMIT = 10


async def get_post_by_id(post_id: int) -> Post:
    post = await select_one(
        DbName.USER,
        "select `post_id`, `user_id`, `date`, `text` from post where post_id = %s",
        (post_id,),
    )
    if not post:
        raise PostNotFound(f"Id: {post_id} not found")
    return Post(*post)


async def get_posts_by_user_id(user_id: int) -> list[Post]:
    posts = await select_all(
        DbName.USER,
        "select `post_id`, `user_id`, `date`, `text` from post where user_id = %s limit %s",
        (user_id, POST_FETCH_LIMIT),
    )
    if not posts:
        raise PostNotFound(f"No posts found")
    return [Post(*post) for post in posts]
