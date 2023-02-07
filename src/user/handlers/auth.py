from aiohttp.web import Request, RouteTableDef
from aiohttp_session import get_session, new_session
from attr import define

from src.user.db_user import (
    AccountNotFound,
    check_password,
    get_account_by_username,
    get_user_id_by_username,
    encrypt_password,
    create_user_account,
    create_profile_for_account,
)
from src.user.models import APIResponse
from src.user.util import structure_request_body, is_username_valid, is_email_valid

from .handlers import api_route_get, api_route_put

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


@define
class CreateAccountRequest:
    username: str
    password: str
    email: str


@define
class CreateAccountResponse:
    @define
    class User:
        user_id: int
        username: str

    user: User


@api_route_get(routes, "/test")
async def test(request: Request):
    session = await get_session(request)
    return APIResponse(session.__dict__)


@api_route_put(routes, "/authenticate")
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

    session = await new_session(request)
    session["user_id"] = user.user_id

    return APIResponse(
        AuthenticateResponse(AuthenticateResponse.User(user.user_id, user.username))
    )


@api_route_put(routes, "/authenticate/create")
async def create_account(request: Request) -> APIResponse:
    req_data: CreateAccountRequest = await structure_request_body(
        request, CreateAccountRequest
    )

    if not is_username_valid(req_data.username):
        return APIResponse("Username is invalid")
    if not is_email_valid(req_data.email):
        return APIResponse("Email is invalid")

    try:
        user = await get_user_id_by_username(req_data.username)
        if user:
            return APIResponse("Username is taken. Please try again.", error=True)
    except AccountNotFound:
        pass

    encrypted_pw = await encrypt_password(req_data.password)
    user_id = await create_user_account(req_data.username, encrypted_pw, req_data.email)
    await create_profile_for_account(user_id, req_data.username, "I'm new here!", "")

    session = await new_session(request)
    session["user_id"] = user_id

    return APIResponse(
        CreateAccountResponse(CreateAccountResponse.User(user_id, req_data.username))
    )
