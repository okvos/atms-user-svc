from aiohttp.web import Request
from attr import define
from cattr import structure
from cattr.errors import ClassValidationError
from orjson import loads

BIO_MAX_CHARS = 255
DISPLAY_NAME_MAX_CHARS = 30


@define
class InvalidRequest(Exception):
    pass


async def structure_request_body(request: Request, cl_type):
    req_json = await request.json(loads=loads)
    req = None
    try:
        req = structure(req_json, cl_type)
    except ClassValidationError:
        raise InvalidRequest()
    except Exception as e:
        print(e)
    if not req:
        print("NO")
    return req
