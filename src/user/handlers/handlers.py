import traceback
from functools import wraps

from aiohttp.web import RouteTableDef, json_response
from aiohttp_session import get_session
from cattr import unstructure

from src.user.models import APIResponse, UserSession
from src.user.util import InvalidRequest


# wrap APIResponse and convert to aiohttp.web.Response
def api_response(
    route_table: RouteTableDef, method: str, path: str, auth: bool = False
):
    def wrapper(handler):
        @wraps(handler)
        async def wrapped(request):
            status = 200

            # check for session to add to request locals
            sess = await get_session(request)
            logged_in = False
            if sess and (user_id := sess.get("user_id")):
                logged_in = True
                request["session"] = UserSession(user_id, sess.get("username"))

            # if auth is required, check and send 401 if applicable
            if auth and not logged_in:
                return json_response(data={"message": "Not authenticated"}, status=401)
            try:
                resp: APIResponse = await handler(request)
            except InvalidRequest:
                status = 400
                resp = APIResponse("Invalid request", success=False, error=True)
                resp_dict = unstructure(resp)
                return json_response(data=resp_dict, status=status)

            except Exception as e:
                # print traceback even though we are catching error
                traceback.print_exc()
                status = 500
                resp = APIResponse(str(e), success=False, error=True)
                resp_dict = unstructure(resp)
                return json_response(data=resp_dict, status=status)

            if resp.error:
                resp.success = False
                resp.response = {"message": resp.response}

            resp_dict = unstructure(resp)
            return json_response(data=resp_dict, status=status)

        getattr(route_table, method)(path)(wrapped)
        return wrapped

    return wrapper


def api_route_get(route_table: RouteTableDef, path: str, auth: bool = False):
    return api_response(route_table, "get", path, auth)


def api_route_post(route_table: RouteTableDef, path: str, auth: bool = False):
    return api_response(route_table, "post", path, auth)


def api_route_put(route_table: RouteTableDef, path: str, auth: bool = False):
    return api_response(route_table, "put", path, auth)


def api_route_delete(route_table: RouteTableDef, path: str, auth: bool = False):
    return api_response(route_table, "delete", path, auth)
