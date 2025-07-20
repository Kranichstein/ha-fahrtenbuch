import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required("speed_sensor"): str,
    vol.Required("gps_latitude"): str,
    vol.Required("gps_longitude"): str,
    vol.Required("battery_sensor"): str,
    vol.Optional("threshold", default=1.0): vol.Coerce(float),
    vol.Optional("file_path", default="fahrtenbuch.csv"): str,
})

class FahrtenbuchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA
            )
        return self.async_create_entry(
            title="Fahrtenbuch",
            data=user_input
        )
