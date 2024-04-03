"""Platform for camera integration."""
from __future__ import annotations

import logging

from .immich_photos import Immich_Photos
import voluptuous as vol

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.camera import (PLATFORM_SCHEMA, Camera, CameraEntityDescription)

from homeassistant.const import CONF_URL, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger("immich_photos")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

CAMERA_TYPE = CameraEntityDescription(
    key="immich_photos", name="Immich Photos", icon="mdi:image"
)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Immich Photos platform."""
    # Add devices
    _LOGGER.info(pformat(config))

    camera_config = {
        "url": config[CONF_URL],
        "api_key": config[CONF_API_KEY]
    }

    add_entities([ImmichPhotosCamera(camera_config)])


class ImmichPhotosCamera(Camera):
    _camera: Immich_Photos

    def __init__(self, camera_config) -> None:
        """Initialize an ImmichPhotos."""
        super().__init__()
        self._camera = Immich_Photos(url=camera_config["url"],
                                     api_key=camera_config["api_key"])
        self._camera.get_next_album()
        self.entity_description = CAMERA_TYPE
        self._attr_native_value = "Cover photo"
        self._attr_frame_interval = 10
        self._attr_is_on = True
        self._attr_is_recording = False
        self._attr_is_streaming = False
        self._attr_unique_id = f"ID-media"
        self._attr_extra_state_attributes = {}

    def camera_image(
            self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        self._camera.get_next_album()
        self._camera.get_next_media()
        return self._camera.get_media_content()

    def update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        self._camera.get_next_album()
        self._camera.get_next_media()
        self._camera.get_media_content()
