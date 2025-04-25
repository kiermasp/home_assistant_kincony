"""The Kincony KC868 integration."""
from __future__ import annotations

import logging
import json
import re
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_DEVICE_ID
import homeassistant.helpers.config_validation as cv
from homeassistant.components.mqtt import async_subscribe

_LOGGER = logging.getLogger(__name__)

DOMAIN = "kincony"
CONF_DEVICE_ID = "device_id"
CONF_INPUTS = "inputs"
CONF_OUTPUTS = "outputs"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICE_ID): cv.string,
    })
})

async def _get_device_state(hass: HomeAssistant, device_id: str) -> dict | None:
    """Get the initial state from MQTT."""
    topic = f"device/{device_id}/STATE"
    
    try:
        # Subscribe to the topic and wait for a message
        message = await async_subscribe(
            hass,
            topic,
            lambda msg: None,
            1,  # QoS
            True,  # Retain
        )
        
        if message and hasattr(message, 'payload'):
            return json.loads(message.payload)
    except Exception as err:
        _LOGGER.error("Error getting initial state: %s", err)
    
    return None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kincony KC868 from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    device_id = entry.data[CONF_DEVICE_ID]
    device_type = entry.data.get("device_type", "KC868_A64")
    
    # Get initial state to determine number of inputs and outputs
    state_message = await _get_device_state(hass, device_id)
    if not state_message:
        _LOGGER.error("Could not get initial state from MQTT")
        return False
    
    # Find all input and output keys
    input_keys = [key for key in state_message.keys() if key.startswith("input")]
    output_keys = [key for key in state_message.keys() if key.startswith("output")]
    
    if not input_keys and not output_keys:
        _LOGGER.error("No input or output keys found in state message")
        return False
    
    # Store the device info and configuration in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "device_id": device_id,
        "device_type": device_type,
        CONF_INPUTS: input_keys,
        CONF_OUTPUTS: output_keys,
    }
    
    # Forward the setup to the binary_sensor and switch platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["binary_sensor", "switch"])
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["binary_sensor", "switch"])
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok 