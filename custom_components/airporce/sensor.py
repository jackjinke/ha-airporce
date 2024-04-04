import logging
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from .const import DOMAIN, DATA_KEY_API, DATA_KEY_GROUPS, DATA_KEY_COORDINATOR


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    groups = hass.data[DOMAIN][entry.entry_id][DATA_KEY_GROUPS]
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_KEY_COORDINATOR]

    # Create sensor entities based on the available data
    sensors = []
    for group in groups:
        for device in group['devices']:
            sensors.extend([
                AirPurifierTempSensor(
                    name="Temperature",
                    unique_id=f"{device['uuid']}-temp",
                    device_id=device['id'],
                    coordinator=coordinator
                ),
                # Repeat for other sensors like PM2.5, PM10, etc.
            ])

    async_add_entities(sensors, update_before_add=True)

class AirPurifierTempSensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = 'mdi:thermometer'

    def __init__(self, name: str, unique_id: str, device_id: str, coordinator: DataUpdateCoordinator):
        super().__init__(coordinator)
        self._unique_id = unique_id
        self._device_id = device_id
        self._name = name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current temperature."""
        return float(self.coordinator.data[self._device_id]['status']["temperature"]) / 10

