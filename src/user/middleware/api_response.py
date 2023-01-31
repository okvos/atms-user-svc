from aiohttp.web import Request, Response, json_response, middleware
from cattr import unstructure

from ..models import APIResponse
from ..util import InvalidRequest


@middleware
async def api_response(request: Request, handler) -> Response:
    status = 200
    try:
        resp: APIResponse = await handler(request)
    except InvalidRequest:
        status = 400
        resp = APIResponse("Invalid request", error=True)
    except Exception as e:
        status = 500
        resp = APIResponse("Unknown error.", error=True)

    if resp.error:
        resp.success = False
        resp.response = {"message": resp.response}
    resp_dict = unstructure(resp)
    return json_response(data=resp_dict, status=status)
