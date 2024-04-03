from .api_types import Album, Media
from .api import ImmichManager

import logging

LOGGER = logging.getLogger(__name__)

class Immich_Photos:
    _album: Album
    _media: Media
    _manager: ImmichManager

    def __init__(self, url: str, api_key: str, shared=True) -> None:
        self._url = url
        self._api_key = api_key
        self._shared = shared
        self._album = Album()
        self._media = Media()
        self._manager = ImmichManager(url=self._url, api_key=self._api_key)

    def get_next_album(self) -> None:
        """ Get next album. By default random and from only shared albums """
        self._album = self._manager.get_random_album(shared=self._shared)

    def get_next_media(self) -> None:
        """ Get next media from album. By default random """
        if self._album == {}:
            self.get_next_album()

        if self._album != {}:
            self._media = self._manager.get_random_media(album_id=self._album['id'])

    def get_media_content(self) -> bytes:
        """ Get media raw content """
        return self._manager.get_media_content(asset_id=self._media['id'])
