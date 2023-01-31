from aiohttp.web import Request, RouteTableDef
from attr import define

from src.user.db_user import (AccountNotFound, check_password,
                              get_account_by_username)
from src.user.models import APIResponse
from src.user.util import structure_request_body

routes = RouteTableDef()


@define
class AuthenticateRequest:
    username: str
    password: str


@define
class AuthenticateResponse:
    @define
    class User:
        user_id: int
        username: str

    user: User


@routes.put("/authenticate")
async def authenticate(request: Request) -> APIResponse:
    req_data: AuthenticateRequest = await structure_request_body(
        request, AuthenticateRequest
    )
    try:
        user = await get_account_by_username(req_data.username)
    except AccountNotFound:
        return APIResponse("Incorrect username and/or password", error=True)

    is_password_correct = await check_password(req_data.password, user.password)
    if not is_password_correct:
        return APIResponse("Incorrect username and/or password", error=True)

    return APIResponse(
        AuthenticateResponse(AuthenticateResponse.User(user.user_id, user.username))
    )
