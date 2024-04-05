""" Immich photos downloader and processor  """
from __future__ import annotations

import io
from PIL import Image

from .api_types import Album, Media
from .api import ImmichManager
from .const import (ORIENTATION_NORMAL,
                    ORIENTATION_TOP_TO_LEFT,
                    ORIENTATION_TOP_TO_RIGHT,
                    ORIENTATION_UPSIDE_DOWN,
                    MEDIA_TYPE_IMAGE)

import logging

_LOGGER = logging.getLogger("immich_photos")


def image2bytes(image: Image) -> bytes:
    """ Convert media from Image to bytes """
    with io.BytesIO() as media_bytes:
        image.save(media_bytes, "JPEG")
        return media_bytes.getvalue()


def rotate_media(media: bytes, orientation: str | None) -> bytes:
    """ Rotate media"""
    _orientation = orientation or ORIENTATION_NORMAL
    _angle = 0
    if _orientation == ORIENTATION_TOP_TO_LEFT:
        _angle = 270
    elif _orientation == ORIENTATION_UPSIDE_DOWN:
        _angle = 180
    elif _orientation == ORIENTATION_TOP_TO_RIGHT:
        _angle = 90

    return image2bytes(Image.open(io.BytesIO(media)).rotate(_angle))


def resize_media(media: bytes, width: int | None = None, height: int | None = None) -> bytes:
    """ Resize media"""
    _width = width or 1024
    _height = height or 512

    return image2bytes(Image.open(io.BytesIO(media)).resize(size=(_width, _height)))


class ImmichPhotos:
    """ Immich album and media downloader"""
    _album: Album
    _media: Media

    def __init__(self, url: str, api_key: str, shared=True, crop=True) -> None:
        self._url = url
        self._api_key = api_key
        self._shared = shared
        self._crop = crop
        self._album = Album()
        self._media = Media()

    @property
    def album(self):
        return self._album

    @property
    def media(self):
        return self._media

    async def get_next_album(self) -> None:
        """ Get next album. By default, get random album and only from shared albums """
        self._album = await ImmichManager(url=self._url, api_key=self._api_key).get_random_album(shared=self._shared)

    async def get_next_media(self) -> None:
        """ Get next media from album. By default random """
        if self._album == {}:
            await self.get_next_album()

        if self._album != {}:
            self._media = await (
                ImmichManager(url=self._url, api_key=self._api_key).get_random_media(album_id=self._album['id']))

    async def get_media_content(self,
                                width: int | None = None,
                                height: int | None = None,
                                media_id: str | None = None) -> bytes | None:
        """ Get media raw content """
        _media_id = media_id or self._media['id']
        _orientation = None
        if self._media != {}:
            _orientation = self._media['mediaMetaData']['orientation']

        _media = await ImmichManager(url=self._url, api_key=self._api_key).get_media_content(media_id=_media_id)

        if self._media['mimeType'] == MEDIA_TYPE_IMAGE:
            # Try to resize
            # try:
            #    _media = resize_media(media=_media, width=width, height=width)
            # except Exception as err:
            #    _LOGGER.error("Unable to rotate media: %s, %s", err, _media_id)

            # Try to rotate
            try:
                _media = rotate_media(media=_media, orientation=_orientation)
            except Exception as err:
                _LOGGER.error("Unable to rotate media: %s, %s", err, _media_id)

        return _media
