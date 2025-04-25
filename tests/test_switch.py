"""Tests for the Kincony KC868 switch platform."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.mqtt import DATA_MQTT

from custom_components.kincony.switch import async_setup_entry, KinconySwitch

@pytest.mark.asyncio
async def test_setup_switches(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test setting up switches."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a list to store added entities
    added_entities = []
    
    # Mock the async_add_entities function
    async def mock_async_add_entities(entities):
        added_entities.extend(entities)
        return True
    
    # Set up the switches
    await async_setup_entry(hass, mock_config_entry, mock_async_add_entities)
    
    # Verify the correct number of entities were created
    assert len(added_entities) == 2
    
    # Verify each entity
    for entity in added_entities:
        assert isinstance(entity, KinconySwitch)
        assert entity._device_type == "KC868_A64"
        assert entity._device_id == "D4D4DAE11EA4"
        assert entity._output_id in ["output1", "output2"]

@pytest.mark.asyncio
async def test_switch_state(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test switch state updates."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a switch
    switch = KinconySwitch(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "output1",
        "Output 1",
    )
    
    # Verify initial state
    assert switch.is_on is False
    
    # Set up subscription
    await switch.async_added_to_hass()
    
    # Mock MQTT message and call the callback
    message = AsyncMock()
    message.payload = json.dumps({"output1": {"value": True}})
    await mock_mqtt.callback(message)
    
    # Verify state was updated
    assert switch.is_on is True

@pytest.mark.asyncio
async def test_switch_turn_on(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt_publish):
    """Test turning on a switch."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a switch
    switch = KinconySwitch(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "output1",
        "Output 1",
    )
    
    # Turn on the switch
    await switch.async_turn_on()
    
    # Verify MQTT message was published
    mock_mqtt_publish.assert_awaited_once_with(
        hass,
        "KC868_A64/D4D4DAE11EA4/SET",
        json.dumps({"output1": {"value": True}}),
        retain=True,
    )

@pytest.mark.asyncio
async def test_switch_turn_off(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt_publish):
    """Test turning off a switch."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a switch
    switch = KinconySwitch(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "output1",
        "Output 1",
    )
    
    # Turn off the switch
    await switch.async_turn_off()
    
    # Verify MQTT message was published
    mock_mqtt_publish.assert_awaited_once_with(
        hass,
        "KC868_A64/D4D4DAE11EA4/SET",
        json.dumps({"output1": {"value": False}}),
        retain=True,
    )

@pytest.mark.asyncio
async def test_switch_cleanup(hass: HomeAssistant, mock_config_entry, mock_hass_data, mock_mqtt):
    """Test switch cleanup."""
    # Set up the test data
    hass.data.update(mock_hass_data)
    
    # Create a switch
    switch = KinconySwitch(
        hass,
        "KC868_A64",
        "D4D4DAE11EA4",
        "output1",
        "Output 1",
    )
    
    # Set up subscription
    await switch.async_added_to_hass()
    
    # Clean up
    await switch.async_will_remove_from_hass()
    
    # Verify unsubscribe was called
    assert switch._unsubscribe is None 