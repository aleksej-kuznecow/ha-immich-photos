""" Immich photos downloader and processor  """
from __future__ import annotations

import io
from datetime import datetime, timedelta
from PIL import Image

from .api_types import Album, Media
from .api import ImmichAPI
from .const import (ORIENTATION_NORMAL,
                    ORIENTATION_TOP_TO_LEFT,
                    ORIENTATION_TOP_TO_RIGHT,
                    ORIENTATION_UPSIDE_DOWN,
                    UPDATE_INTERVAL_ALBUM,
                    UPDATE_INTERVAL_IMAGE)

from homeassistant.config_entries import ConfigEntry

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
    """ Immich album and media downloader """
    album: Album = Album()
    media: Media = Media()
    current_media_timestamp: datetime | None = None
    current_album_timestamp: datetime | None = None

    def __init__(self, config: ConfigEntry) -> None:
        self._url = config['url']
        self._api_key = config['api_key']
        self._shared = config['shared_albums']
        self._update_interval: tuple = (config['update_interval']['album'], config['update_interval']['image'])

    async def get_next_album(self) -> None:
        """ Get next album. By default, get random album and only from shared albums """
        self.album = await ImmichAPI(url=self._url, api_key=self._api_key).get_random_album(shared=self._shared)

    async def get_next_media(self) -> None:
        """ Get next media from album. By default random """
        if self.album == {}:
            _LOGGER.error("Album is not defined")
        else:
            self.media = await (
                ImmichAPI(url=self._url, api_key=self._api_key).get_random_media(album_id=self.album['id']))

    async def download(self, size: tuple | None) -> None:
        """ Download image """
        _current_media = await (ImmichAPI(url=self._url,
                                          api_key=self._api_key)
                                .get_media_content(media_id=self.media['id']))

        # Try to rotate
        try:
            _orientation = None
            if self.media != {}:
                _orientation = self.media['mediaMetaData']['orientation']
            _current_media = rotate_media(media=_current_media, orientation=_orientation)
        except Exception as err:
            _LOGGER.error("Unable to rotate media: %s, %s", err, self.media['id'])

        return _current_media

    async def update_album(self) -> None:
        """ Update album. If update interval equal 0 sec then update each time """
        if self.current_album_timestamp is None:
            await self.get_next_album()
            self.current_album_timestamp = datetime.now()
            _LOGGER.debug("First album %s", self.album['id'])
        else:
            if (datetime.now() - self.current_album_timestamp) > self._update_interval[UPDATE_INTERVAL_ALBUM]:
                await self.get_next_album()
                self.current_album_timestamp = datetime.now()
                _LOGGER.debug("Album %s", self.album['id'])

    async def update_media(self, size: tuple | None) -> None:
        """ Update media. If update interval not defined then do not update (this parameter is mandatory! """
        if self.current_media_timestamp is None:
            await self.get_next_media()
            self.current_media_timestamp = datetime.now()
            _LOGGER.debug("First media %s", self.media['id'])
        else:
            if (datetime.now() - self.current_media_timestamp) > self._update_interval[UPDATE_INTERVAL_IMAGE]:
                await self.get_next_media()
                self.current_media_timestamp = datetime.now()
                _LOGGER.debug("Media %s", self.media['id'])

    async def refresh(self, size: tuple | None) -> None:
        """ Refresh data """
        await self.update_album()
        await self.update_media(size)

        return await self.download(size)

