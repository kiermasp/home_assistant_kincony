"""Config flow for Kincony KC868 integration."""
from __future__ import annotations

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import mqtt
from homeassistant.components.mqtt import async_subscribe
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service_info.mqtt import MqttServiceInfo

from .const import DOMAIN, CONF_DEVICE_TYPE, CONF_INPUTS, CONF_OUTPUTS

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

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_device: dict[str, Any] | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
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
                # Find all input and output keys
                input_keys = [key for key in state.keys() if key.startswith("input")]
                output_keys = [key for key in state.keys() if key.startswith("output")]
                
                if not input_keys and not output_keys:
                    errors["base"] = "no_entities"
                else:
                    return self.async_create_entry(
                        title=f"{device_type} {device_id}",
                        data={
                            CONF_DEVICE_ID: device_id,
                            CONF_DEVICE_TYPE: device_type,
                            CONF_INPUTS: input_keys,
                            CONF_OUTPUTS: output_keys,
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

    async def async_step_mqtt(self, discovery_info: MqttServiceInfo) -> config_entries.ConfigFlowResult:
        """Handle MQTT discovery."""
        if not discovery_info.payload:
            return self.async_abort(reason="mqtt_missing_payload")
    
        # Extract device_id and device_type from MQTT topic
        topic_parts = discovery_info.topic.split('/')
        if len(topic_parts) >= 3:
            device_type = topic_parts[0]
            device_id = topic_parts[1]
        else:
            return self.async_abort(reason="invalid_discovery_info")

        # Check if device is already configured
        await self.async_set_unique_id(f"{device_type}_{device_id}")
        self._abort_if_unique_id_configured()

        try:
            # Parse the payload to get state
            state = json.loads(discovery_info.payload)
            
            # Find all input and output keys
            input_keys = [key for key in state.keys() if key.startswith("input")]
            output_keys = [key for key in state.keys() if key.startswith("output")]
            
            if not input_keys and not output_keys:
                return self.async_abort(reason="no_entities")

            # Store the discovered device info
            self._discovered_device = {
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_TYPE: device_type,
                CONF_INPUTS: input_keys,
                CONF_OUTPUTS: output_keys,
            }

            # Show confirmation form
            return await self.async_step_confirm()

        except json.JSONDecodeError:
            return self.async_abort(reason="invalid_payload")

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None) -> config_entries.ConfigFlowResult:
        """Handle the confirmation step."""
        if not self._discovered_device:
            return self.async_abort(reason="discovery_failed")

        if user_input is not None:
            return self.async_create_entry(
                title=f"{self._discovered_device[CONF_DEVICE_TYPE]} {self._discovered_device[CONF_DEVICE_ID]}",
                data=self._discovered_device,
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "device_type": str(self._discovered_device[CONF_DEVICE_TYPE]),
                "device_id": str(self._discovered_device[CONF_DEVICE_ID]),
                "inputs": str(len(self._discovered_device[CONF_INPUTS])),
                "outputs": str(len(self._discovered_device[CONF_OUTPUTS])),
            },
            data_schema=vol.Schema({}),
        ) 