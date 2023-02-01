from aiohttp.web import Request, RouteTableDef

from src.user.db_user import (AccountNotFound, get_account_by_id,
                              get_profile_by_username)
from src.user.handlers.handlers import api_route_get
from src.user.models import APIResponse

routes = RouteTableDef()


@api_route_get(routes, "/user/{id}")
async def main(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    try:
        user = await get_account_by_id(user_id)
    except AccountNotFound:
        return APIResponse("User not found", error=True)
    return APIResponse({"user": user})


@api_route_get(routes, "/profile/{username}")
async def main(request: Request) -> APIResponse:
    username = str(request.match_info.get("username"))
    try:
        profile = await get_profile_by_username(username)
    except AccountNotFound:
        return APIResponse("Profile not found", error=True)
    return APIResponse({"profile": profile})
