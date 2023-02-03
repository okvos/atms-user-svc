from aiohttp.web import Request, RouteTableDef

from src.user.db_feed import (
    PostNotFound,
    get_post_by_id,
    get_posts_by_user_id,
    like_post,
    unlike_post,
    is_post_liked_by_user_id,
    are_posts_liked_by_user_id,
    is_user_id_following_user_id,
    follow_user,
    unfollow_user,
)
from src.user.db_user import get_profiles_by_user_ids
from src.user.handlers.handlers import api_route_delete, api_route_get, api_route_post
from src.user.models import APIResponse, UserSession

routes = RouteTableDef()


@api_route_get(routes, "/post/{id}")
async def get_post(request: Request) -> APIResponse:
    post_id = int(request.match_info.get("id"))

    try:
        post = await get_post_by_id(post_id)
    except PostNotFound:
        return APIResponse("Post not found", error=True)
    if sess := request.get("session"):
        post.is_liked = await is_post_liked_by_user_id(post_id, sess.user_id)
    return APIResponse({"post": post})


@api_route_get(routes, "/user/{id}/posts")
async def get_posts(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    try:
        posts = await get_posts_by_user_id(user_id)
    except PostNotFound:
        return APIResponse("Posts not found", error=True)

    user_ids = {post.user_id for post in posts}
    user_profiles = await get_profiles_by_user_ids(user_ids)

    posts_liked = tuple()
    if sess := request.get("session"):
        post_ids = [post.post_id for post in posts]
        if post_ids:
            posts_liked = await are_posts_liked_by_user_id(post_ids, sess.user_id)

    for post in posts:
        if post.post_id in posts_liked:
            post.is_liked = True
        post.username = user_profiles.get(post.user_id).username

    return APIResponse({"posts": posts})


@api_route_post(routes, "/post/{id}/like", auth=True)
async def post_like(request: Request) -> APIResponse:
    sess: UserSession = request.get("session")
    post_id = int(request.match_info.get("id"))

    liked = await like_post(sess.user_id, post_id)

    return APIResponse({}, success=liked)


@api_route_delete(routes, "/post/{id}/like", auth=True)
async def delete_like(request: Request) -> APIResponse:
    sess: UserSession = request.get("session")
    post_id = int(request.match_info.get("id"))

    await unlike_post(sess.user_id, post_id)

    return APIResponse({})


@api_route_get(routes, "/user/{id}/follow", auth=True)
async def is_following(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    sess: UserSession = request.get("session")

    if user_id == sess.user_id:
        return APIResponse("Can not follow self", error=True)

    is_following_resp = await is_user_id_following_user_id(sess.user_id, user_id)
    return APIResponse({"following": is_following_resp})


@api_route_post(routes, "/user/{id}/follow", auth=True)
async def follow_user_req(request: Request) -> APIResponse:

    user_id = int(request.match_info.get("id"))
    sess: UserSession = request.get("session")

    if user_id == sess.user_id:
        return APIResponse("Can not follow self", error=True)

    did_follow = await follow_user(sess.user_id, user_id)
    return APIResponse({}, success=did_follow)


@api_route_delete(routes, "/user/{id}/follow", auth=True)
async def unfollow_user_req(request: Request) -> APIResponse:

    user_id = int(request.match_info.get("id"))
    sess: UserSession = request.get("session")

    if user_id == sess.user_id:
        return APIResponse("Can not follow self", error=True)

    await unfollow_user(sess.user_id, user_id)
    return APIResponse({})
