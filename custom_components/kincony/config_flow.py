"""Config flow for Kincony KC868 integration."""
from __future__ import annotations

import logging
import json
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.components import mqtt
from homeassistant.components.mqtt import async_subscribe
from homeassistant.const import CONF_DEVICE_ID

from .const import DOMAIN, CONF_DEVICE_TYPE

_LOGGER = logging.getLogger(__name__)

async def _get_device_state(hass: HomeAssistant, device_id: str) -> dict | None:
    """Get the initial state from MQTT."""
    device_type = "KC868_A64"  # Default device type
    topic = f"{device_type}/{device_id}/STATE"

    if not await mqtt.async_wait_for_mqtt_client(hass):
        _LOGGER.error("MQTT integration is not available")
        return None

    try:
        # Subscribe to the topic and wait for a message
        message = await async_subscribe(
            hass,
            topic,
            lambda msg: None,
            1,  # QoS
            None,  # encoding parameter instead of retain
        )
        
        if message and hasattr(message, 'payload'):
            return json.loads(message.payload)
    except Exception as err:
        _LOGGER.error("Error getting initial state: %s", err)
    
    return None

class KinconyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kincony KC868."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device_type = user_input.get(CONF_DEVICE_TYPE, "KC868_A64")

            # Check if device is already configured
            await self.async_set_unique_id(f"{device_type}_{device_id}")
            self._abort_if_unique_id_configured()

            # Try to get device state
            state = await _get_device_state(self.hass, device_id)
            if state is None:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"{device_type} {device_id}",
                    data={
                        CONF_DEVICE_ID: device_id,
                        CONF_DEVICE_TYPE: device_type,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_ID): str,
                vol.Optional(CONF_DEVICE_TYPE, default="KC868_A64"): str,
            }),
            errors=errors,
        )

    async def async_step_mqtt(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle MQTT discovery."""
        device_id = discovery_info.get("device_id")
        device_type = discovery_info.get("device_type", "KC868_A64")

        if not device_id:
            return self.async_abort(reason="invalid_discovery_info")

        # Check if device is already configured
        await self.async_set_unique_id(f"{device_type}_{device_id}")
        self._abort_if_unique_id_configured()

        # Try to get device state
        state = await _get_device_state(self.hass, device_id)
        if state is None:
            return self.async_abort(reason="cannot_connect")

        return self.async_create_entry(
            title=f"{device_type} {device_id}",
            data={
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_TYPE: device_type,
            },
        ) 