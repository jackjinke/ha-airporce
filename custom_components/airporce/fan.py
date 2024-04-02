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

    _on_mode = 'Smart'
    _off_mode = 'Off'
    _off_mode_ids = [10, 12]    # Appearently both means the device is off
    _mode_mapping = {"Smart": 2, "Sleep": 20, "Off": 10}

    def __init__(self, name: str, unique_id: str, device_id: str, api: AirPorceApi):
        self._name = name
        self._unique_id = unique_id
        self.device_id = device_id
        self.api = api
        self._preset_mode = self._off_mode # TODO: remove after all modes are supported
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
        if cur_mode_id in self._off_mode_ids:
            self._is_on = False
            self._preset_mode = self._off_mode
        else:
            self._is_on = True
            for key, value in self._mode_mapping.items():
                if value == cur_mode_id:
                    self._preset_mode = key
                    break

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
        return list(self._mode_mapping.keys())

    @property
    def preset_mode(self):
        return self._preset_mode

    def turn_on(self, **kwargs):
        # Implement turning on the purifier and setting it to Smart mode by default
        self.set_preset_mode(self._on_mode)

    def turn_off(self, **kwargs):
        # Implement turning off the purifier
        self.set_preset_mode(self._off_mode)

    def set_preset_mode(self, preset_mode):
        mode_id = self._mode_mapping.get(preset_mode)
        if mode_id is not None:
            result = self.api.set_mode(self.device_id, mode_id)
            if result:
                if preset_mode == self._off_mode:
                    self._is_on = False
                else:
                    self._is_on = True
                    self._preset_mode = preset_mode
                self.async_write_ha_state()  # Inform HA about the update
                _LOGGER.info(f"Successfully set mode to {preset_mode}")
            else:
                # Handle API call failure
                _LOGGER.error(f"Failed to set mode to {preset_mode}")