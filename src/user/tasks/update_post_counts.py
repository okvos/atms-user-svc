from src.user.db import DbName, select_one, update


async def update_post_comment_count(post_id: int):
    count_comments = await select_one(
        DbName.FEED,
        "select count(1) from post_comment where post_id = %s",
        (post_id,),
    )

    num_comments = count_comments[0] if count_comments else 0

    await update(
        DbName.FEED,
        "update `post` set `num_comments` = %s where `post_id` = %s",
        (
            num_comments,
            post_id,
        ),
    )


async def update_post_like_count(post_id: int):
    count_likes = await select_one(
        DbName.FEED,
        "select count(1) from post_like where post_id = %s",
        (post_id,),
    )

    num_likes = count_likes[0] if count_likes else 0
    await update(
        DbName.FEED,
        "update `post` set `num_likes` = %s where `post_id` = %s",
        (
            num_likes,
            post_id,
        ),
    )
