from src.user.db import select_one, DbName, update


async def update_follower_count(user_id: int):
    count_followers = await select_one(
        DbName.FEED,
        "select count(1) from following where following_id = %s",
        (user_id,),
    )

    num_followers = count_followers[0] if count_followers else 0

    await update(
        DbName.USER,
        "update `profile` set `follower_count` = %s where `user_id` = %s",
        (
            num_followers,
            user_id,
        ),
    )
