""" API for Immich """
from __future__ import annotations

import logging
import aiohttp
from urllib.parse import urljoin
# from homeassistant.exceptions import HomeAssistantError

from random import randint

from .api_types import UserItem, AlbumItem, MediaItem, MediaMetadata
from .const import MEDIA_TYPE_IMAGE

_LOGGER = logging.getLogger("immich_photos")


def create_user_item_from_json(request: dict) -> UserItem | None:
    """" Create User object item by JSON string """
    try:
        return UserItem(id=request['id'],
                        email=request['email'],
                        name=request['name'],
                        status=request['status'])
    except Exception as expt:
        _LOGGER.error("User object item created with errors: %s", expt)
        return None


def create_album_item_from_json(request: dict) -> AlbumItem | None:
    """" Create Album object item by JSON string """
    try:
        return AlbumItem(id=request['id'],
                         title=request['albumName'],
                         shared=request['shared'],
                         mediaItemsCount=request['assetCount'])
    except Exception as expt:
        _LOGGER.error("Album object item created with errors: %s", expt)
        return None


def create_media_item_from_json(request: dict) -> MediaItem | None:
    """"Creates Media object item by JSON string"""
    try:
        _mediaMetaData = MediaMetadata(creationTime=request['fileCreatedAt'],
                                       width=request['exifInfo']['exifImageWidth'],
                                       height=request['exifInfo']['exifImageHeight'],
                                       orientation=request['exifInfo']['orientation'],
                                       cameraMake=request['exifInfo']['make'],
                                       cameraModel=request['exifInfo']['model'])
        return MediaItem(id=request['id'],
                         mimeType=request['type'],
                         description=request['exifInfo']['description'],
                         filename=request['originalPath'],
                         mediaMetaData=_mediaMetaData)
    except Exception as expt:
        _LOGGER.error("Media object item created with errors: %s", expt)
        return None


class ImmichAPI:
    """" Immich API class """

    def __init__(self, url: str, api_key: str) -> None:
        self.url = url
        self.api_key = api_key

    async def _api_wrapper(self, api_path: str, return_json: bool = True):
        headers_accept = 'application/json'
        if not return_json:
            headers_accept = 'application/octet-stream'

        payload = {}
        headers = {
            'Accept': headers_accept,
            'x-api-key': self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=urljoin(self.url, api_path), headers=headers, data=payload) as response:
                    if response.status != 200:
                        _LOGGER.error("Immich API error: http status=%d", response.status)
                        return False

                    if return_json:
                        return await response.json()
                    else:
                        return await response.read()
        except aiohttp.ClientError as exception:
            _LOGGER.error("Immich API connection error: %s", exception)
            return False

    async def ping(self) -> bool:
        """ Check if API available """
        api_path = "/api/server-info/ping"

        ping_info: dict = await self._api_wrapper(api_path=api_path)
        if ping_info:
            return ping_info['res'] == 'pong'

        return False

    async def get_my_user_info(self) -> UserItem:
        """" Return current user info """
        api_path = "/api/users/me"

        return await self._api_wrapper(api_path=api_path)

    async def get_all_albums(self, shared=False) -> list:
        """" Return a list of all Albums """
        api_path = "/api/albums"
        if shared:
            api_path = api_path + "?shared=true"

        _album_list: dict = await self._api_wrapper(api_path=api_path)
        if _album_list:
            result: list[AlbumItem] = [create_album_item_from_json(_album) for _album in _album_list]
            return result

        return []

    async def get_random_album(self, shared=False) -> AlbumItem | None:
        """"Get random Album"""
        all_albums = await self.get_all_albums(shared)
        if len(all_albums) > 0:
            return all_albums[randint(1, len(all_albums)) - 1]
        else:
            return None

    async def get_album_info(self, album_id: str | None) -> AlbumItem | None:
        """Get Album info by ID"""
        if album_id is None:
            return None
        api_path = f"/api/albums/{album_id}"

        _album_info: dict = await self._api_wrapper(api_path=api_path)
        if _album_info:
            return create_album_item_from_json(_album_info)
        return None

    async def get_album_media_items(self, album_id: str | None) -> list:
        """" Get list of all Media in the Album """
        if album_id is None:
            return []

        api_path = f"/api/albums/{album_id}"

        _album_info: dict = await self._api_wrapper(api_path=api_path)
        if _album_info:
            result: list[MediaItem] = [
                create_media_item_from_json(media)
                for media in _album_info['assets'] if media['type'] == MEDIA_TYPE_IMAGE
            ]
            return result
        return []

    async def get_media_info(self, media_id: str | None) -> MediaItem | None:
        """" Get media info """
        if media_id is None:
            return None
        api_path = f"/api/asset/{media_id}"

        _media_info: dict = await self._api_wrapper(api_path=api_path)
        if _media_info:
            return create_media_item_from_json(_media_info)
        return None

    async def get_random_media(self, search_param: str | list[MediaItem] | None) -> MediaItem | None:
        """"Returns random media from an Album"""
        _media = MediaItem()
        if search_param is None:
            return None
        media_item_list: list[MediaItem] = []

        if isinstance(search_param, str):
            media_item_list = await self.get_album_media_items(search_param)
        else:
            media_item_list = search_param

        if len(media_item_list) > 0:
            return media_item_list[randint(1, len(media_item_list)) - 1]
        else:
            return None

    async def get_media_content(self, media_id: str) -> bytes | None:
        if media_id is None:
            return None
        api_path = f"/api/assets/{media_id}/thumbnail?size=fullsize"

        _media_content: bytes = await self._api_wrapper(api_path=api_path, return_json=False)
        if _media_content:
            return _media_content
        return None
