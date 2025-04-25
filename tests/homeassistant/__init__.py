"""Mock Home Assistant package."""
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class HomeAssistant:
    """Mock Home Assistant class."""
    data: Dict[str, Any] = None
    states: Dict[str, Any] = None
    config: Dict[str, Any] = None 