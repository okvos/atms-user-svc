from attr import define


@define
class APIResponse:
    response: dict | str | None
    success: bool = True
    error: bool | None = False


@define
class UserSession:
    user_id: int
    username: str


@define
class ProfileSummary:
    user_id: int
    username: str
