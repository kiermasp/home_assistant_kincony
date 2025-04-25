"""Mock Home Assistant for testing."""
from unittest.mock import MagicMock, AsyncMock

class MockMQTTClient:
    """Mock MQTT client."""
    def __init__(self):
        """Initialize the mock MQTT client."""
        self.connected = True
        self.async_publish = AsyncMock()
        self.async_subscribe = AsyncMock()

class MockMQTTData:
    """Mock MQTT data."""
    def __init__(self):
        """Initialize the mock MQTT data."""
        self.client = MockMQTTClient()
        self.config = {}

class MockHomeAssistant:
    """Mock Home Assistant instance."""
    def __init__(self):
        """Initialize the mock Home Assistant."""
        self.data = {
            "mqtt": MockMQTTData()
        }
        self.states = {}
        self.config = {}
        self.bus = MagicMock()
        self.bus.async_fire = AsyncMock()
        self.config_entries = MagicMock()
        self.config_entries.async_has_entries = MagicMock(return_value=True)
        self.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        self.config_entries.async_unload_platforms = AsyncMock(return_value=True)

def get_test_home_assistant():
    """Get a test Home Assistant instance."""
    return MockHomeAssistant() 