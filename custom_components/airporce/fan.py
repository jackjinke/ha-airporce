import logging
from .api import AirPorceApi
from .const import DOMAIN, DATA_KEY_API, DATA_KEY_GROUPS, DATA_KEY_COORDINATOR
from datetime import timedelta
from homeassistant.components.fan import FanEntity, SUPPORT_PRESET_MODE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up fans for each device from a config entry."""
    # Retrieve data from `hass.data`
    api = hass.data[DOMAIN][entry.entry_id][DATA_KEY_API]
    groups = hass.data[DOMAIN][entry.entry_id][DATA_KEY_GROUPS]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]
    
    # Create a list of fan entities
    entities = [
        AirPurifierFan(
            name=f"{device['model']}-{device['id']}",
            unique_id=device['uuid'],
            device_id=device['id'],
            api=api,
            coordinator=coordinator
        )
        for group in groups
        for device in group['devices']
    ]

    # Add the fan entities
    async_add_entities(entities, update_before_add=True)


class AirPurifierFan(FanEntity, CoordinatorEntity):

    _preset_modes = ["Manual", "Smart", "Sleep"]

    def __init__(self, name: str, unique_id: str, device_id: str, api: AirPorceApi, coordinator: DataUpdateCoordinator):
        CoordinatorEntity.__init__(self, coordinator)
        self._name = name
        self._unique_id = unique_id
        self.device_id = device_id
        self.api = api

    def current_mode_id(self):
        return self.coordinator.data[self.device_id]['control']['mode']

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
        mode_id = self.current_mode_id()
        return not (mode_id >= 10 and mode_id < 20)

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        mode_id = self.current_mode_id()
        if mode_id == 1:
            return 'Manual'
        elif mode_id == 2:
            return 'Smart'
        elif mode_id >= 20 and mode_id < 30:
            return 'Sleep'
        else:
            return None

    def turn_on(self, **kwargs):
        self.api.set_mode(self.device_id, 0)
        self.hass.async_create_task(self.coordinator.async_refresh())

    def turn_off(self, **kwargs):
        self.api.set_mode(self.device_id, 10)
        self.hass.async_create_task(self.coordinator.async_refresh())

    def set_preset_mode(self, preset_mode: str):
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
        self.hass.async_create_task(self.coordinator.async_refresh())
