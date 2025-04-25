"""Test configuration for the Kincony KC868 integration."""
import json
from unittest.mock import AsyncMock, patch

import pytest

from .mock_hass import get_test_home_assistant
from custom_components.kincony import DOMAIN

@pytest.fixture
def hass():
    """Mock Home Assistant instance."""
    return get_test_home_assistant()

@pytest.fixture
def mock_mqtt():
    """Mock MQTT subscription."""
    mock = AsyncMock()
    
    async def mock_subscribe(hass, topic, callback, qos=0, retain=False):
        # Store the callback for later use
        mock.callback = callback
        # Return a mock unsubscribe function
        mock_unsubscribe = AsyncMock()
        mock_unsubscribe.return_value = None
        return mock_unsubscribe

    mock.side_effect = mock_subscribe
    return mock

@pytest.fixture
def mock_mqtt_publish():
    """Mock MQTT publish."""
    mock = AsyncMock()
    mock.return_value = None
    return mock

@pytest.fixture
def mock_mqtt_message():
    """Mock MQTT message."""
    return {
        "input1": {"value": False},
        "input2": {"value": True},
        "output1": {"value": False},
        "output2": {"value": True},
        "adc1": {"value": 0},
        "adc2": {"value": 0},
        "adc3": {"value": 0},
        "adc4": {"value": 0}
    }

@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    class MockConfigEntry:
        """Mock config entry class."""
        def __init__(self):
            """Initialize mock config entry."""
            self.entry_id = "test_entry"
            self.domain = DOMAIN
            self.title = "Test Device"
            self.data = {
                "device_type": "KC868_A64",
                "device_id": "D4D4DAE11EA4",
            }
            self.source = "user"
            self.async_unload_platforms = AsyncMock(return_value=True)
    
    return MockConfigEntry()

@pytest.fixture
def mock_hass_data():
    """Mock hass.data."""
    return {
        DOMAIN: {
            "test_entry": {
                "device_type": "KC868_A64",
                "device_id": "D4D4DAE11EA4",
                "inputs": ["input1", "input2"],
                "outputs": ["output1", "output2"],
            }
        }
    } 