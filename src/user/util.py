from aiohttp.web import Request
from attr import define
from cattr import structure
from cattr.errors import ClassValidationError
from orjson import loads
from re import compile, fullmatch

BIO_MAX_CHARS = 255
DISPLAY_NAME_MAX_CHARS = 30

USERNAME_MAX_CHARS = 25
USERNAME_MIN_CHARS = 2
USERNAME_REGEX = compile("^[A-Za-z0-9]+(?:[ ;\*\.!_-][A-Za-z0-9!\.\*]+)*$")

EMAIL_MIN_CHARS = 6
EMAIL_MAX_CHARS = 255
EMAIL_REGEX = compile(
    r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
)

UPLOAD_URL_KEY_REGEX = compile(r"([A-Za-z0-9\-_=/.])+(png|jpg|gif|jpeg|webp)")

POST_TEXT_MIN_CHARS = 1
POST_TEXT_MAX_CHARS = 1000


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


def is_email_valid(email: str) -> bool:
    if not (EMAIL_MIN_CHARS <= len(email) <= EMAIL_MAX_CHARS):
        return False
    return fullmatch(EMAIL_REGEX, email) is not None


def is_username_valid(username: str) -> bool:
    if not (USERNAME_MIN_CHARS <= len(username) <= USERNAME_MAX_CHARS):
        return False
    return fullmatch(USERNAME_REGEX, username) is not None


def is_upload_url_key_valid(key: str) -> bool:
    return fullmatch(UPLOAD_URL_KEY_REGEX, key) is not None
