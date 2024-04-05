""" API for Immich """
from __future__ import annotations

import logging
import aiohttp
# from homeassistant.exceptions import HomeAssistantError

from random import randint

from .api_types import Album, Media, MediaMetadata
from .const import MEDIA_TYPE_IMAGE

_LOGGER = logging.getLogger("immich_photos")


def create_album_from_json(request: dict) -> Album:
    """" Create Album object by JSON string """
    try:
        return Album(id=request['id'],
                     title=request['albumName'],
                     shared=request['shared'],
                     mediaItemsCount=request['assetCount'])
    except Exception:
        return Album()


def create_media_from_json(request: dict) -> Media:
    """"Creates Media object by JSON string"""
    try:
        _mediaMetaData = MediaMetadata(creationTime=request['fileCreatedAt'],
                                       width=request['exifInfo']['exifImageWidth'],
                                       height=request['exifInfo']['exifImageHeight'],
                                       orientation=request['exifInfo']['orientation'],
                                       cameraMake=request['exifInfo']['make'],
                                       cameraModel=request['exifInfo']['model']
                                       )
        return Media(id=request['id'],
                     mimeType=request['type'],
                     description=request['exifInfo']['description'],
                     filename=request['originalPath'],
                     mediaMetaData=_mediaMetaData
                     )
    except Exception:
        return Media()


class ImmichManager:
    """" Immich API class """

    def __init__(self, url: str, api_key: str) -> None:
        self.url = url
        self.api_key = api_key

    async def ping(self) -> bool:
        """ Check if API available """
        api_path = "/api/server-info/ping"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return False

                    ping_info: dict = await response.json()
                    return ping_info['res'] == 'pong'
        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return False

    async def get_all_albums(self, shared=False) -> list:
        """" Return a list of all Albums """
        api_path = "/api/album"
        if shared:
            api_path = api_path + "?shared=true"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return []

                    _album_list: dict = await response.json()
                    result: list[Album] = [create_album_from_json(_album) for _album in _album_list]
                    return result

        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return []

    async def get_random_album(self, shared=False) -> Album:
        """"Get random Album"""
        all_albums = await self.get_all_albums(shared)
        _album = Album()
        if len(all_albums) > 0:
            _album = all_albums[randint(1, len(all_albums)) - 1]

        return _album

    async def get_album_info(self, album_id: str | None) -> Album:
        """Get Album info by ID"""
        if album_id is None:
            return Album()
        api_path = "/api/album/" + album_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return Album()

                    _album_info: dict = await response.json()
                    return create_album_from_json(_album_info)

        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return Album()

    async def get_album_media_items(self, album_id: str | None) -> list:
        """" Get list of all Media in the Album """
        if album_id is None:
            return []

        api_path = "/api/album/" + album_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return []

                    _album_info: dict = await response.json()
                    result: list[Media] = [
                        create_media_from_json(media)
                        for media in _album_info['assets'] if media['type'] == MEDIA_TYPE_IMAGE
                    ]
                    return result

        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return []

    async def get_media_info(self, media_id: str | None) -> Media:
        """" Get media info """
        if media_id is None:
            return Media()
        api_path = "/api/asset/" + media_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return Media()

                    _media_info: dict = await response.json()
                    return create_media_from_json(_media_info)

        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return Media()

    async def get_random_media(self, album_id: str | None) -> Media:
        """"Returns random media from an Album"""
        _media = Media()
        if album_id is None:
            return _media

        media_list = await self.get_album_media_items(album_id)

        if len(media_list) > 0:
            _media = media_list[randint(1, len(media_list)) - 1]

        return _media

    async def get_media_content(self, media_id: str) -> bytes | None:
        """Returns Media content in bytes."""
        api_path = "/api/asset/file/" + media_id
        payload = {}
        headers = {
            'Accept': 'application/octet-stream',
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.url + api_path, headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return None

                    return await response.read()

        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return None

    # class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
