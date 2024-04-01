from .fan import AirPurifierFan
from .api import AirPorceApi
from .const import DOMAIN, CONFIG_KEY_TOKEN, DATA_KEY_API, DATA_KEY_GROUPS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry


async def async_setup(hass: HomeAssistant, config: dict):
    # Setup your component here
    return True


async def async_setup_entry(hass, entry):
    """Set up from a config entry."""
    # Read the token from the entry's data
    # Initialize your API client with the provided token
    api = AirPorceApi(token=entry.data[CONFIG_KEY_TOKEN])
    
    # Fetch the groups
    groups = await hass.async_add_executor_job(api.list_groups)
    
    if groups is None:
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_KEY_API: api,
        DATA_KEY_GROUPS: groups
    }

    # Forward the setup to your platform(s)
    for platform in ["fan", "sensor"]:  # Adjust based on your available platforms
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True