from aiohttp.web import Request, RouteTableDef

from src.user.db_feed import PostNotFound, get_post_by_id, get_posts_by_user_id
from src.user.models import APIResponse

routes = RouteTableDef()


@routes.get("/post/{id}")
async def get_post(request: Request) -> APIResponse:
    post_id = int(request.match_info.get("id"))

    try:
        post = await get_post_by_id(post_id)
    except PostNotFound:
        return APIResponse("Post not found", error=True)
    return APIResponse({"post": post})


@routes.get("/user/{id}/posts")
async def get_posts(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    try:
        posts = await get_posts_by_user_id(user_id)
    except PostNotFound:
        return APIResponse("Posts not found", error=True)
    return APIResponse({"posts": posts})
