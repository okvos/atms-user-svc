from aiohttp.web import Request, Response, json_response, middleware
from cattr import unstructure

from ..models import APIResponse


@middleware
async def api_response(request: Request, handler) -> Response:
    resp: APIResponse = await handler(request)
    if resp.error:
        resp.success = False
        resp.response = {"message": resp.response}
    resp_dict = unstructure(resp)
    return json_response(data=resp_dict)
