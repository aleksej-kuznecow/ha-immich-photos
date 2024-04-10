""" Immich photos downloader and processor  """
from __future__ import annotations

import io
from datetime import datetime, timedelta
from PIL import Image

from .api_types import AlbumItem, MediaItem
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
    current_album_item: AlbumItem | None = None
    current_media_item_list: list[MediaItem] = []
    current_media_item: MediaItem | None = None
    current_media_item_timestamp: datetime | None = None
    current_album_item_timestamp: datetime | None = None

    def __init__(self, config: ConfigEntry) -> None:
        self._url = config['url']
        self._api_key = config['api_key']
        self._shared = config['shared_albums']
        self._update_interval: tuple = (config['update_interval']['album'], config['update_interval']['image'])

    async def get_next_album(self) -> None:
        """ Get next album. By default, get random album and only from shared albums """
        self.current_album_item = await (ImmichAPI(url=self._url, api_key=self._api_key).
                                         get_random_album(shared=self._shared))
        if self.current_album_item is None:
            _LOGGER.error("There are no albums")
        else:
            self.current_media_item_list = await (ImmichAPI(url=self._url, api_key=self._api_key).
                                                  get_album_media_items(self.current_album_item['id']))

    async def get_next_media(self) -> None:
        """ Get next media from album. By default random """
        if self.current_album_item is None:
            _LOGGER.error("Album is not defined")
        else:
            self.current_media_item = await (ImmichAPI(url=self._url, api_key=self._api_key).
                                             get_random_media(self.current_media_item_list))

    async def download(self, size: tuple | None) -> None:
        """ Download image """
        _current_media = await (ImmichAPI(url=self._url, api_key=self._api_key).
                                get_media_content(media_id=self.current_media_item['id']))

        # Try to rotate
        try:
            _orientation = None
            if self.current_media_item is not None:
                _orientation = self.current_media_item['mediaMetaData']['orientation']
            _current_media = rotate_media(media=_current_media, orientation=_orientation)
        except Exception as err:
            _LOGGER.error("Unable to rotate media: %s, %s", err, self.current_media_item['id'])

        return _current_media

    async def update_album(self) -> None:
        """ Update album. If update interval equal 0 sec then update each time """
        if self.current_album_item_timestamp is None:
            await self.get_next_album()
            self.current_album_item_timestamp = datetime.now()
            _LOGGER.debug("First album %s", self.current_album_item['id'])
        else:
            if (datetime.now() - self.current_album_item_timestamp) > self._update_interval[UPDATE_INTERVAL_ALBUM]:
                await self.get_next_album()
                self.current_album_item_timestamp = datetime.now()
                _LOGGER.debug("Album %s", self.current_album_item['id'])

    async def update_media(self, size: tuple | None) -> None:
        """ Update media. If update interval not defined then do not update (this parameter is mandatory! """
        if self.current_media_item is None:
            await self.get_next_media()
            self.current_media_item_timestamp = datetime.now()
            _LOGGER.debug("First media %s", self.current_media_item['id'])
        else:
            if (datetime.now() - self.current_media_item_timestamp) > self._update_interval[UPDATE_INTERVAL_IMAGE]:
                await self.get_next_media()
                self.current_media_item_timestamp = datetime.now()
                _LOGGER.debug("Media %s", self.current_media_item['id'])

    async def refresh(self, size: tuple | None) -> None:
        """ Refresh data """
        await self.update_album()
        await self.update_media(size)

        return await self.download(size)

