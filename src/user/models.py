from attr import define


@define
class APIResponse:
    response: dict | None = ""
    success: bool = True
    error: str | None = None
