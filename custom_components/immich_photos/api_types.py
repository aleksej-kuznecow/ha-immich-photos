from typing import TypedDict, Optional


class MediaMetadataPhoto(TypedDict):
    """Metadata that is specific to a photo, such as, ISO, focal length and exposure time.
    Some of these fields may be null or not included."""

    focalLength: Optional[float]
    apertureFNumber: Optional[float]
    isoEquivalent: Optional[int]
    exposureTime: Optional[str]


class MediaMetadataVideo(TypedDict):
    """Metadata that is specific to a video, for example, fps and processing status.
    Some of these fields may be null or not included."""

    fps: Optional[float]
    status: Optional[str]


class MediaMetadata(TypedDict):
    """Metadata for a media item."""

    creationTime: str
    width: int
    height: int
    orientation: int
    cameraMake: Optional[str]
    cameraModel: Optional[str]
    photo: Optional[MediaMetadataPhoto]
    video: Optional[MediaMetadataVideo]


class Media(TypedDict):
    """Representation of a media item (such as a photo or video)."""

    id: str | None
    description: Optional[str]
    mimeType: str
    filename: str
    mediaMetaData: Optional[MediaMetadata]


class Album(TypedDict):
    id: str | None
    title: str | None
    shared: bool | None
    mediaItemsCount: int | None
