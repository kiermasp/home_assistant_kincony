"""Mock binary sensor component."""
from typing import Any

class BinarySensorEntity:
    """Mock binary sensor entity."""
    def __init__(self) -> None:
        """Initialize the binary sensor."""
        self._state = False

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self._state 