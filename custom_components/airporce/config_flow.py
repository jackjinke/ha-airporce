from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import DOMAIN, CONFIG_KEY_TOKEN


class AirPorceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        # Define the data schema for the form
        data_schema = vol.Schema({
            vol.Required(CONFIG_KEY_TOKEN): str,
        })

        if user_input is not None:
            # Validate user input
            token = user_input[CONFIG_KEY_TOKEN]
            # Here you would typically validate the token by attempting a test API call
            valid = True  # Replace with actual validation logic
            if valid:
                # If the token is valid, proceed to create the config entry
                return self.async_create_entry(title="API token", data=user_input)
            else:
                # If the token is invalid, show an error message
                errors["base"] = "invalid_token"

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AirPorceOptionsFlowHandler(config_entry)


class AirPorceOptionsFlowHandler(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle the options flow."""
        if user_input is not None:
            # Update options and finish the flow
            return self.async_create_entry(title="AirPorce", data=user_input)

        # Define options schema (if you have options to configure)
        options_schema = vol.Schema({
            vol.Optional(CONFIG_KEY_TOKEN, default=self.config_entry.options.get(CONFIG_KEY_TOKEN)): str,
        })

        return self.async_show_form(step_id="user", data_schema=options_schema)
