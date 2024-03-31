import logging
from .api import AirPorceApi
from .const import DOMAIN
from homeassistant.components.fan import FanEntity, SUPPORT_PRESET_MODE, PRESET_MODES
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the fan platform for AirPurifierFan."""
    # Retrieve the API client
    api = hass.data[DOMAIN][entry.entry_id]

    # Now you can use `api_client` to interact with your device's API
    # TODO: Fetch name, unique ID and device ID.
    async_add_entities([AirPurifierFan(api)])


class AirPurifierFan(FanEntity):

    mode_mapping = {"Smart": 2, "Sleep": 20, "Off": 10}

    def __init__(self, name: str, unique_id: str, device_id: str, api: AirPorceApi):
        self._name = name
        self._unique_id = unique_id
        self.device_id = device_id
        self.api = api
        self._is_on = False
        self._preset_mode = None
        self._preset_modes = self.mode_mapping.keys()

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        return self._is_on

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        return self._preset_mode

    def turn_on(self, **kwargs):
        # Implement turning on the purifier and setting it to Smart mode by default
        self._is_on = True
        self.set_preset_mode("Smart")

    def turn_off(self, **kwargs):
        # Implement turning off the purifier
        self._is_on = False
        self.set_preset_mode("Off")

    def set_preset_mode(self, preset_mode):
        mode_id = self.mode_mapping.get(preset_mode)
        if mode_id is not None:
            result = self.api.set_mode(self.device_id, mode_id)
            if result:
                self._preset_mode = preset_mode
                self._is_on = mode_id != 10  # Assuming mode 10 is 'Off'
                self.async_write_ha_state()  # Inform HA about the update
                _LOGGER.info(f"Successfully set mode to {preset_mode}")
            else:
                # Handle API call failure
                _LOGGER.error(f"Failed to set mode to {preset_mode}")