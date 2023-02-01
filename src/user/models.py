from attr import define


@define
class APIResponse:
    response: any = ""
    success: bool = True
    error: bool | None = None
