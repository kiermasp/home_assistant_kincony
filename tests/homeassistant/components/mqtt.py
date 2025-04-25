"""Mock MQTT component."""
from typing import Any, Callable

async def async_subscribe(hass: Any, topic: str, msg_callback: Callable, qos: int = 0, retain: bool = False) -> None:
    """Mock MQTT subscribe."""
    pass

async def async_publish(hass: Any, topic: str, payload: str, retain: bool = False) -> None:
    """Mock MQTT publish."""
    pass 