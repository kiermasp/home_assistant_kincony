"""The KinCony KC868 integration."""
from __future__ import annotations

import logging
import json
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import mqtt
from homeassistant.components.mqtt import async_subscribe
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_DEVICE_TYPE, CONF_DEVICE_ID, CONF_INPUTS, CONF_OUTPUTS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up KinCony KC868 from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Setting up KinCony KC868 from config entry")
    
    device_id = entry.data[CONF_DEVICE_ID]
    device_type = entry.data.get(CONF_DEVICE_TYPE)
    input_keys = entry.data.get(CONF_INPUTS, [])
    output_keys = entry.data.get(CONF_OUTPUTS, [])
    
    if not input_keys and not output_keys:
        _LOGGER.error("No input or output keys found in configuration")
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