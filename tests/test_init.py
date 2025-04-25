"""Tests for the Kincony KC868 integration."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.mqtt import DATA_MQTT

from custom_components.kincony import async_setup_entry, DOMAIN, async_unload_entry

@pytest.mark.asyncio
async def test_setup_entry(hass: HomeAssistant, mock_mqtt, mock_mqtt_message, mock_config_entry):
    """Test setting up the integration."""
    # Mock MQTT subscription
    async def mock_subscribe(hass, topic, callback, qos=0, retain=False):
        # Create a mock message with the test data
        message = AsyncMock()
        message.payload = json.dumps(mock_mqtt_message)
        # Call the callback with the message
        if callback:
            await callback(message)
        # Return a mock unsubscribe function
        mock_unsubscribe = AsyncMock()
        mock_unsubscribe.return_value = None
        return mock_unsubscribe

    mock_mqtt.side_effect = mock_subscribe

    # Set up the integration
    with patch("homeassistant.components.mqtt.async_subscribe", new=mock_mqtt):
        result = await async_setup_entry(hass, mock_config_entry)

        # Verify setup was successful
        assert result is True

        # Verify the data was stored correctly
        assert mock_config_entry.entry_id in hass.data[DOMAIN]
        config = hass.data[DOMAIN][mock_config_entry.entry_id]
        assert config["device_id"] == "D4D4DAE11EA4"
        assert config["device_type"] == "KC868_A64"
        assert config["inputs"] == ["input1", "input2"]
        assert config["outputs"] == ["output1", "output2"]

@pytest.mark.asyncio
async def test_setup_entry_no_mqtt_message(hass: HomeAssistant, mock_mqtt, mock_config_entry):
    """Test setting up the integration with no MQTT message."""
    # Mock MQTT to return None
    async def mock_subscribe(hass, topic, callback, qos=0, retain=False):
        return AsyncMock()

    with patch("homeassistant.components.mqtt.async_subscribe", side_effect=mock_subscribe):
        # Set up the integration
        result = await async_setup_entry(hass, mock_config_entry)
        
        # Verify setup failed
        assert result is False
        
        # Verify hass.data was not updated
        assert DOMAIN not in hass.data or not hass.data[DOMAIN]

@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, mock_config_entry):
    """Test unloading the integration."""
    # Set up test data
    hass.data[DOMAIN] = {
        mock_config_entry.entry_id: {
            "device_type": "KC868_A64",
            "device_id": "D4D4DAE11EA4",
            "inputs": ["input1", "input2"],
            "outputs": ["output1", "output2"],
        }
    }
    
    # Unload the integration
    result = await async_unload_entry(hass, mock_config_entry)
    
    # Verify unload was successful
    assert result is True
    
    # Verify hass.data was cleaned up
    assert mock_config_entry.entry_id not in hass.data[DOMAIN] 