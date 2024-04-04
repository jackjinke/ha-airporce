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

    _preset_modes = ["Manual", "Smart", "Sleep"]

    def __init__(self, name: str, unique_id: str, device_id: str, api: AirPorceApi):
        self._name = name
        self._unique_id = unique_id
        self.device_id = device_id
        self.api = api
        self._is_on = False
        self._preset_mode = None
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
        if cur_mode_id >= 10 and cur_mode_id < 20:
            self._is_on = False
            self._preset_mode = None
            return
        self._is_on = True
        if cur_mode_id == 1:
            self._preset_mode = 'Manual'
        elif cur_mode_id == 2:
            self._preset_mode = 'Smart'
        elif cur_mode_id >= 20 and cur_mode_id < 30:
            self._preset_mode = 'Sleep'
        else:
            self._preset_mode = None

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
        return self._preset_modes

    @property
    def preset_mode(self):
        return self._preset_mode

    def turn_on(self, **kwargs):
        self.api.set_mode(self.device_id, 0)
        self._is_on = True
        self.async_write_ha_state()

    def turn_off(self, **kwargs):
        self.api.set_mode(self.device_id, 10)
        self._is_on = False
        self.async_write_ha_state()

    def set_preset_mode(self, preset_mode):
        if preset_mode not in self._preset_modes:
            _LOGGER.error(f"Trying to set an invalid preset mode: {preset_mode}")
            return
        match preset_mode:
            case 'Manual':
                self.api.set_mode(self.device_id, 1)
            case 'Smart':
                self.api.set_mode(self.device_id, 2)
            case 'Sleep':
                self.api.set_mode(self.device_id, 20)
        self._preset_mode = preset_mode
        self.async_write_ha_state()
