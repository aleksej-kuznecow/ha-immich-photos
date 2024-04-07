"""Platform for camera integration."""
from __future__ import annotations

import logging

from .immich_photos import ImmichPhotos
from .const import (CONF_UPDATE_INTERVAL,
                    CONF_UPDATE_INTERVAL_ALBUM,
                    CONF_UPDATE_INTERVAL_IMAGE,
                    CONF_SHARED_ALBUMS)
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
    vol.Required(CONF_URL): cv.url,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_UPDATE_INTERVAL): {vol.Optional(CONF_UPDATE_INTERVAL_ALBUM): cv.time_period_seconds,
                                         vol.Required(CONF_UPDATE_INTERVAL_IMAGE): cv.time_period_seconds},
    vol.Required(CONF_SHARED_ALBUMS): cv.boolean
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
        "api_key": config[CONF_API_KEY],
        "update_interval": {"album": config[CONF_UPDATE_INTERVAL][CONF_UPDATE_INTERVAL_ALBUM],
                            "image": config[CONF_UPDATE_INTERVAL][CONF_UPDATE_INTERVAL_IMAGE]},
        "shared_albums": config[CONF_SHARED_ALBUMS]
    }

    add_entities([ImmichPhotosCamera(camera_config)])


class ImmichPhotosCamera(Camera):
    def __init__(self, camera_config) -> None:
        """Initialize an ImmichPhotos."""
        super().__init__()
        self._camera = ImmichPhotos(camera_config)
        self.entity_description = CAMERA_TYPE
        self._attr_native_value = "Cover photo"
        self._attr_frame_interval = 10
        self._attr_is_on = True
        self._attr_is_recording = False
        self._attr_is_streaming = False
        self._attr_unique_id = "immich_photos"
        self._attr_extra_state_attributes = {}

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        """Return a still image response from the camera."""
        return await self._camera.refresh(size=(width, height))

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        return await self._camera.refresh()
