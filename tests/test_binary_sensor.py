"""Tests for the Kincony KC868 binary sensor platform."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.mqtt import DATA_MQTT

from custom_components.kincony.binary_sensor import async_setup_entry, KinconyBinarySensor

@pytest.mark.asyncio
async def test_setup_binary_sensors(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test setting up binary sensors."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a list to store added entities
    added_entities = []
    
    # Mock the async_add_entities function
    async def mock_async_add_entities(entities):
        added_entities.extend(entities)
        return True
    
    # Set up the binary sensors
    await async_setup_entry(hass, mock_config_entry, mock_async_add_entities)
    
    # Verify the correct number of entities were created
    assert len(added_entities) == 2
    
    # Verify each entity
    for entity in added_entities:
        assert isinstance(entity, KinconyBinarySensor)
        assert entity._device_type == "KC868_A64"
        assert entity._device_id == "D4D4DAE11EA4"
        assert entity._input_id in ["input1", "input2"]

@pytest.mark.asyncio
async def test_binary_sensor_state(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test binary sensor state updates."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a binary sensor
    sensor = KinconyBinarySensor(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "input1",
        "Input 1",
    )
    
    # Verify initial state
    assert sensor.is_on is False
    
    # Set up subscription
    await sensor.async_added_to_hass()
    
    # Mock MQTT message and call the callback
    message = AsyncMock()
    message.payload = json.dumps({"input1": {"value": True}})
    await mock_mqtt.callback(message)
    
    # Verify state was updated
    assert sensor.is_on is True

@pytest.mark.asyncio
async def test_binary_sensor_cleanup(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test binary sensor cleanup."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a binary sensor
    sensor = KinconyBinarySensor(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "input1",
        "Input 1",
    )
    
    # Set up subscription
    await sensor.async_added_to_hass()
    
    # Clean up
    await sensor.async_will_remove_from_hass()
    
    # Verify unsubscribe was called
    assert sensor._unsubscribe is None 