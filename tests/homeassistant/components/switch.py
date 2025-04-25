"""Mock switch component."""
from typing import Any

class SwitchEntity:
    """Mock switch entity."""
    def __init__(self) -> None:
        """Initialize the switch."""
        self._state = False

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self._state = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        self._state = False 