from requests import request
import json
from random import randint
from .api_types import Album, Media, MediaMetadata, MediaMetadataPhoto, MediaMetadataVideo


class ImmichManager:
    """" Immich API class """
    url: str
    api_key: str

    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key

    def ping(self) -> bool:
        """ Check if API available """
        api_path = "/api/server-info/ping"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        result = False
        try:
            if json.loads(request("GET", self.url + api_path, headers=headers,
                                  data=payload).text)["res"] == "pong":
                result = True
        except Exception:
            result = False

        return result

    def create_album_from_json(self, json_str: str) -> Album:
        """" Create Album object by JSON string """
        try:
            request = json_str

            return Album(id=request['id'],
                         title=request['albumName'],
                         shared=request['shared'],
                         mediaItemsCount=request['assetCount'])
        except Exception:
            return Album()

    def get_all_albums(self, shared=False) -> list:
        """" Return a list of all Albums """
        api_path = "/api/album"
        if shared:
            api_path = api_path + "?shared=true"

        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        result = []
        for _album in json.loads(request("GET",
                                         self.url + api_path,
                                         headers=headers,
                                         data=payload).text):
            result.append(self.create_album_from_json(_album))
        return result

    def get_random_album(self, shared=False) -> Album:
        """"Get random Album"""
        all_albums = self.get_all_albums(shared)
        random_album_number = randint(1, len(all_albums))

        return all_albums[random_album_number - 1]

    def get_album_info(self, album_id: str) -> Album:
        """Get Album info by ID"""
        if album_id is None:
            return Album()
        api_path = "/api/album/" + album_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        return self.create_album_from_json(json.loads(request("GET",
                                                              self.url + api_path,
                                                              headers=headers,
                                                              data=payload).text))

    def create_media_from_json(self, json_str: str) -> Media:
        """"Creates Media object by JSON string"""
        try:
            request = json_str
            _photo = MediaMetadataPhoto()
            _video = MediaMetadataVideo()
            if request['type'] == 'IMAGE':
                _photo['focalLength'] = request['exifInfo']['focalLength']
                _photo['apertureFNumber'] = request['exifInfo']['fNumber']
                _photo['isoEquivalent'] = request['exifInfo']['iso']
                _photo['exposureTime'] = request['exifInfo']['exposureTime']

            _mediaMetaData = MediaMetadata(creationTime=request['fileCreatedAt'],
                                           width=request['exifInfo']['exifImageWidth'],
                                           height=request['exifInfo']['exifImageHeight'],
                                           orientation=request['exifInfo']['orientation'],
                                           cameraMake=request['exifInfo']['make'],
                                           cameraModel=request['exifInfo']['model'],
                                           photo=_photo,
                                           video=_video
                                           )
            return Media(id=request['id'],
                         mimeType=request['type'],
                         description=request['exifInfo']['description'],
                         filename=request['originalPath'],
                         mediaMetaData=_mediaMetaData
                         )
        except Exception:
            return Media()

    def get_album_media_items(self, album_id: str) -> list:
        """" Get list of all Media in the Album """
        if album_id is None:
            return []

        api_path = "/api/album/" + album_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        result = []
        for _media in json.loads(request("GET",
                                         self.url + api_path,
                                         headers=headers,
                                         data=payload).text)["assets"]:
            result.append(self.create_media_from_json(_media))
        return result

    def get_media_info(self, asset_id: str) -> Media:
        """" Get media info """
        if asset_id is None:
            return Media()
        api_path = "/api/asset/" + asset_id
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.api_key
        }
        return self.create_media_from_json(json.loads(request("GET",
                                                              self.url + api_path,
                                                              headers=headers,
                                                              data=payload).text))

    def get_random_media(self, album_id: str) -> Media:
        """"Returns random media from an Album"""
        if album_id is None:
            return Media()

        media_list = self.get_album_media_items(album_id)
        random_media_number = randint(1, len(media_list))
        return media_list[random_media_number - 1]

    def get_media_content(self, asset_id: str) -> bytes:
        """Returns Media content in bytes."""
        api_path = "/api/asset/file/" + asset_id
        payload = {}
        headers = {
            'Accept': 'application/octet-stream',
            'x-api-key': self.api_key
        }
        return request("GET", self.url + api_path, headers=headers, data=payload).content
