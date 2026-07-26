"""Config flow for the experimental P20 live-position integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import CALIBRATION_KEYS, DOMAIN


class P20LivePositionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure one P20 live-position sensor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create the single experimental entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(
                title="P20 Pro 实时位置",
                data={key: float(user_input[key]) for key in CALIBRATION_KEYS},
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(key): str for key in CALIBRATION_KEYS}),
        )
