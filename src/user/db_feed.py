import asyncio
from enum import Enum, unique
from typing import Optional

from attr import define
from pymysql.err import IntegrityError

from src.user.db import (
    DbName,
    attrs_to_db_fields,
    delete_one,
    insert_one,
    select_all,
    select_one,
)
from src.user.tasks.update_follower_count import update_follower_count


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
    username: str = ""


@define
class PostLike:
    post_id: int
    user_id: int


@define
class Following:
    followee_id: int
    follower_id: int


@define
class PostComment:
    @unique
    class Visibility(int, Enum):
        VISIBLE = 0
        DELETED = 1
        HIDDEN = 2

    post_id: int
    comment_id: int
    user_id: int
    text: str
    date: int
    visibility: Visibility


COMMENT_DB_KEYS = attrs_to_db_fields(PostComment)


POST_FETCH_LIMIT = 10
COMMENT_FETCH_LIMIT = 5


async def get_post_by_id(post_id: int) -> Post:
    post = await select_one(
        DbName.FEED,
        "select `post_id`, `user_id`, `date`, `text` from `post` where `post_id` = %s",
        (post_id,),
    )
    if not post:
        raise PostNotFound(f"Id: {post_id} not found")
    return Post(*post)


async def get_posts_by_user_id(user_id: int) -> list[Post]:
    posts = await select_all(
        DbName.FEED,
        "select `post_id`, `user_id`, `date`, `text` from `post` where `user_id` = %s order by `date` desc limit %s",
        (user_id, POST_FETCH_LIMIT),
    )
    if not posts:
        raise PostNotFound(f"No posts found")
    return [Post(*post) for post in posts]


async def like_post(user_id: int, post_id: int) -> bool:
    try:
        await insert_one(
            DbName.FEED,
            "insert into `post_like` (`user_id`, `post_id`) values (%s, %s)",
            (user_id, post_id),
        )
    except IntegrityError:
        return False
    return True


async def unlike_post(user_id: int, post_id: int):
    await delete_one(
        DbName.FEED,
        "delete from `post_like` where `user_id` = %s and `post_id` = %s",
        (user_id, post_id),
    )


async def is_post_liked_by_user_id(post_id: int, user_id: int) -> bool:
    res = await select_one(
        DbName.FEED,
        "select 1 from `post_like` where `post_id` = %s and `user_id` = %s",
        (post_id, user_id),
    )
    return res is not None


async def are_posts_liked_by_user_id(post_ids: list[int], user_id: int) -> tuple[int]:
    post_ids_string = ",".join(["%s"] * len(post_ids))
    res = await select_all(
        DbName.FEED,
        f"select `post_id` from `post_like` where `post_id` in ({post_ids_string}) and `user_id` = %s",
        (*post_ids, user_id),
    )
    return tuple(int(post[0]) for post in res if res)


async def is_user_id_following_user_id(follower_id: int, following_id: int) -> bool:
    is_following = await select_one(
        DbName.FEED,
        "select 1 from `following` where `follower_id` = %s and `following_id` = %s",
        (follower_id, following_id),
    )
    return is_following is not None


async def follow_user(user_id: int, following_id: int) -> bool:
    try:
        await insert_one(
            DbName.FEED,
            "insert into `following` (`follower_id`, `following_id`) values (%s, %s)",
            (user_id, following_id),
        )
    except IntegrityError:
        return False
    asyncio.create_task(update_follower_count(following_id))
    return True


async def unfollow_user(follower_id: int, following_id: int):
    await delete_one(
        DbName.FEED,
        "delete from `following` where `follower_id` = %s and `following_id` = %s",
        (follower_id, following_id),
    )
    asyncio.create_task(update_follower_count(following_id))


async def create_post(user_id: int, text: str) -> int:
    post_id = await insert_one(
        DbName.FEED,
        "insert into `post` (`user_id`, `date`, `text`) values (%s, UNIX_TIMESTAMP(), %s)",
        (user_id, text),
        return_last_id=True,
    )
    return post_id


async def get_comments_by_post_id(
    post_id: int, last_id: Optional[int] = None
) -> list[PostComment]:
    limit = COMMENT_FETCH_LIMIT
    query = f"select {COMMENT_DB_KEYS} from `post_comment` where `post_id` = %s"
    values = [post_id]

    # if no last_id is present, this is the first fetch for a post, so we only display the most recent comment
    if not last_id:
        limit = 1
    else:
        query += " and `comment_id` > %s"
        values.append(last_id)
    query += " limit %s"
    values.append(limit)
    comments = await select_all(DbName.FEED, query, tuple(values))
    return [PostComment(*comment) for comment in comments]


async def create_comment(post_id: int, user_id: int, text: str) -> int:
    comment_id = await insert_one(
        DbName.FEED,
        "insert into `post_comment` (`user_id`, `date`, `text`, `post_id`) values (%s, UNIX_TIMESTAMP(), %s, %s)",
        (user_id, text, post_id),
        return_last_id=True,
    )
    return comment_id


async def set_comment_visibility(
    comment_id: int, user_id: int, visibility: PostComment.Visibility
):
    await insert_one(
        DbName.FEED,
        "update `post_comment` set `visibility` = %s where user_id = %s and comment_id = %s",
        (visibility.value, user_id, comment_id),
    )
