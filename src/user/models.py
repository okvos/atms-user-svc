from attr import define


@define
class APIResponse:
    response: dict
    success: bool = True
    error: bool | None = None
