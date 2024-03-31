from .fan import AirPurifierFan
from .api import AirPorceApi
from .const import DOMAIN, CONFIG_PARAM_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


async def async_setup(hass: HomeAssistant, config: dict):
    # Setup your component here
    return True


async def async_setup_entry(hass, entry):
    """Set up from a config entry."""
    # Read the token from the entry's data
    token = entry.data[CONFIG_PARAM_TOKEN]

    # Initialize your API client with the token
    api = AirPorceApi(token=token)

    # You can store the client in `hass.data` for use in your platform (e.g., fan, sensor)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api

    # Set up your platform(s). This example assumes a fan platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "fan")
    )

    return True