from os import getenv

from aiohttp.web import Request, RouteTableDef
from attr import define
from enum import unique, Enum

from src.common.upload_s3 import generate_presigned_url
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
    create_post,
)
from src.user.db_user import get_profiles_by_user_ids
from src.user.handlers.handlers import api_route_delete, api_route_get, api_route_post
from src.user.models import APIResponse, UserSession
from secrets import token_urlsafe

from src.user.util import (
    structure_request_body,
    POST_TEXT_MAX_CHARS,
    POST_TEXT_MIN_CHARS,
)

routes = RouteTableDef()


@define
class UploadImageRequest:
    @unique
    class ImageTypes(str, Enum):
        PNG = "png"
        JPG = "jpg"
        GIF = "gif"

    image_type: ImageTypes


@define
class UploadImageResponse:
    url: str
    key: str


@define
class CreatePostRequest:
    text: str


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


@api_route_post(routes, "/feed/create", auth=True)
async def create_feed_post(request: Request) -> APIResponse:
    req_data: CreatePostRequest = await structure_request_body(
        request, CreatePostRequest
    )
    sess: UserSession = request.get("session")

    if not (POST_TEXT_MIN_CHARS <= len(req_data.text) <= POST_TEXT_MAX_CHARS):
        return APIResponse(
            f"Your post should be between {POST_TEXT_MIN_CHARS} and {POST_TEXT_MAX_CHARS} characters",
            error=True,
        )

    post_id = await create_post(sess.user_id, req_data.text)
    return APIResponse({"post_id": post_id})


@api_route_post(routes, "/upload-image", auth=True)
async def upload_image(request: Request) -> APIResponse:
    req_data: UploadImageRequest = await structure_request_body(
        request, UploadImageRequest
    )

    random_image_id = token_urlsafe(16)
    key = (
        random_image_id[0:2]
        + "/"
        + random_image_id[2:4]
        + "/"
        + random_image_id
        + f".{req_data.image_type.value}"
    )

    presigned_url = generate_presigned_url(getenv("AWS_UPLOAD_BUCKET"), key)
    return APIResponse(UploadImageResponse(presigned_url, key))
