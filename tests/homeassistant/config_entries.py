"""Mock config entries module."""
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class ConfigEntry:
    """Mock config entry class."""
    entry_id: str
    domain: str
    title: str
    data: Dict[str, Any]
    source: str 