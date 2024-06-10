""" API types for integration """
from typing import TypedDict, Optional

class UserItem(TypedDict):
    """ User data """

    id: str
    email: str
    name: str
    status: str             
    
class MediaMetadata(TypedDict):
    """ Metadata for a media item """

    creationTime: str
    width: int
    height: int
    orientation: int | None
    cameraMake: Optional[str]
    cameraModel: Optional[str]


class MediaItem(TypedDict):
    """ Representation of a media item """

    id: str | None
    description: Optional[str]
    mimeType: str
    filename: str
    mediaMetaData: Optional[MediaMetadata]


class AlbumItem(TypedDict):
    """ Representation of an album item """
    id: str | None
    title: str | None
    shared: bool | None
    mediaItemsCount: int | None
