from aiohttp.web import Request, RouteTableDef
from attr import define

from src.user.db_user import (
    AccountNotFound,
    get_account_by_id,
    update_user_profile,
    get_user_id_by_username,
    get_profile_by_user_id,
)
from src.user.handlers.handlers import api_route_get, api_route_put
from src.user.models import APIResponse, UserSession
from src.user.util import structure_request_body, BIO_MAX_CHARS, DISPLAY_NAME_MAX_CHARS

routes = RouteTableDef()


@define
class UpdateProfileRequest:
    bio: str
    display_name: str
    header_image_url: str


@api_route_get(routes, "/user/{id}")
async def get_user(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    try:
        user = await get_account_by_id(user_id)
    except AccountNotFound:
        return APIResponse("User not found", error=True)
    return APIResponse({"user": user})


@api_route_get(routes, "/profile/{username}")
async def get_profile(request: Request) -> APIResponse:
    username = str(request.match_info.get("username"))
    try:
        user_id = await get_user_id_by_username(username)
    except AccountNotFound:
        return APIResponse("User not found", error=True)
    profile = await get_profile_by_user_id(user_id)
    return APIResponse({"profile": profile})


@api_route_put(routes, "/user/profile", auth=True)
async def update_profile(request: Request) -> APIResponse:
    req_data: UpdateProfileRequest = await structure_request_body(
        request, UpdateProfileRequest
    )
    sess: UserSession = request.get("session")

    if len(req_data.bio) > BIO_MAX_CHARS:
        return APIResponse(
            f"Bio should be {BIO_MAX_CHARS} characters or less", error=True
        )

    if len(req_data.display_name) > DISPLAY_NAME_MAX_CHARS:
        return APIResponse(
            f"Display name should be {DISPLAY_NAME_MAX_CHARS} characters or less",
            error=True,
        )

    # todo: add validation for header url, probably make it upload to s3 and then set header_img_url as a key

    await update_user_profile(sess.user_id, req_data.display_name, req_data.bio)
    return APIResponse({}, success=True)
