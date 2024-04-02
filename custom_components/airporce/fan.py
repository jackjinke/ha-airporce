import logging
from .api import AirPorceApi
from .const import DOMAIN, DATA_KEY_API, DATA_KEY_GROUPS
from datetime import timedelta
from homeassistant.components.fan import FanEntity, SUPPORT_PRESET_MODE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up fans for each device from a config entry."""
    # Retrieve data from `hass.data`
    api = hass.data[DOMAIN][entry.entry_id][DATA_KEY_API]
    groups = hass.data[DOMAIN][entry.entry_id][DATA_KEY_GROUPS]
    
    # Create a list of fan entities
    entities = [
        AirPurifierFan(
            name=f"{device['model']}-{device['id']}",
            unique_id=device['uuid'],
            device_id=device['id'],
            api=api
        )
        for group in groups
        for device in group['devices']
    ]

    # Add the fan entities
    async_add_entities(entities, update_before_add=True)


class AirPurifierFan(FanEntity):

    mode_mapping = {"Smart": 2, "Sleep": 20, "Off": 10}

    def __init__(self, name: str, unique_id: str, device_id: str, api: AirPorceApi):
        self._name = name
        self._unique_id = unique_id
        self.device_id = device_id
        self.api = api
        self.async_update()

    def update(self):
        """Fetch new state data for this entity."""
        status = self.api.get_status(self.device_id)
        if status:
            self.update_status(status)

    async def async_update(self):
        """Fetch new state data for this entity."""
        status = await self.hass.async_add_executor_job(
            self.api.get_status, self.device_id
        )
        if status:
            self.update_status(status)

    def update_status(self, status):
        cur_mode_id = status['data']['control']['mode']
        self._preset_mode = cur_mode_id
        self._is_on = cur_mode_id != self.mode_mapping['Off']

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def supported_features(self):
        return SUPPORT_PRESET_MODE

    @property
    def is_on(self):
        return self._is_on

    @property
    def preset_modes(self):
        return list(self.mode_mapping.keys())

    @property
    def preset_mode(self):
        return self._preset_mode

    def turn_on(self, **kwargs):
        # Implement turning on the purifier and setting it to Smart mode by default
        self.set_preset_mode("Smart")

    def turn_off(self, **kwargs):
        # Implement turning off the purifier
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