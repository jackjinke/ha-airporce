from homeassistant import config_entries
import voluptuous as vol
from .api import AirPorceApi
from .const import DOMAIN, CONFIG_KEY_TOKEN


class AirPorceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    api = AirPorceApi() # This API instance does not have token

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            response = await self.hass.async_add_executor_job(
                self.api.send_login_sms, user_input['phone_number']
            )
            if response:
                # Store phone number for next step and go to the next step
                self.context['phone_number'] = user_input['phone_number']
                return await self.async_step_verify_code()
            else:
                errors['base'] = 'sms_send_error'

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required('phone_number'): str,
            }),
            errors=errors,
        )

    async def async_step_verify_code(self, user_input=None):
        errors = {}
        phone_number = self.context['phone_number']

        if user_input is not None:
            # Assuming `verify_sms_code` is a method to call your API to verify the SMS code
            response = await self.hass.async_add_executor_job(
                self.api.user_login, phone_number, user_input['sms_code']
            )
            if response:
                # Success, use the token for your API client creation
                token = response['data']['token']
                return self.async_create_entry(title=f"User: {phone_number}", data={CONFIG_KEY_TOKEN: token})
            else:
                errors['base'] = 'invalid_code'

        return self.async_show_form(
            step_id='verify_code',
            data_schema=vol.Schema({
                vol.Required('sms_code'): str,
            }),
            errors=errors,
        )
