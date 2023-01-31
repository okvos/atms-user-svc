from aiohttp.web import Request, RouteTableDef

from src.user.db_user import AccountNotFound, get_account_by_id
from src.user.models import APIResponse

routes = RouteTableDef()


@routes.get("/user/{id}")
async def main(request: Request) -> APIResponse:
    user_id = int(request.match_info.get("id"))
    try:
        user = await get_account_by_id(user_id)
    except AccountNotFound:
        return APIResponse("User not found", error=True)
    return APIResponse({"user": user})
