from functools import wraps

from aiohttp.web import RouteTableDef, json_response
from cattr import unstructure

from src.user.models import APIResponse
from src.user.util import InvalidRequest


# wrap APIResponse and convert to aiohttp.web.Response
def api_response(route_table: RouteTableDef, method: str, path: str):
    def wrapper(handler):
        @wraps(handler)
        async def wrapped(request):
            status = 200
            try:
                resp: APIResponse = await handler(request)
            except InvalidRequest:

                status = 400
                resp = APIResponse("Invalid request", success=False, error=True)
                resp_dict = unstructure(resp)
                return json_response(data=resp_dict, status=status)

            except Exception as e:
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


def api_route_get(route_table: RouteTableDef, path: str):
    return api_response(route_table, "get", path)


def api_route_post(route_table: RouteTableDef, path: str):
    return api_response(route_table, "post", path)


def api_route_put(route_table: RouteTableDef, path: str):
    return api_response(route_table, "put", path)
