from enum import Enum, unique

from attr import define

from ...models import ProfileSummary


@define
class UploadImageRequest:
    @unique
    class ImageTypes(str, Enum):
        PNG = "png"
        JPG = "jpg"
        GIF = "gif"

    image_type: ImageTypes


@define
class UploadImageResponse:
    url: str
    key: str


@define
class CreatePostRequest:
    text: str


@define
class Comment:
    comment_id: int
    author: ProfileSummary
    text: str
    date: int


@define
class CreateCommentRequest:
    text: str
