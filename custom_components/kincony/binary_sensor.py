"""The KinCony KC868 binary sensor platform."""
from __future__ import annotations

import logging
import json
from typing import Any, Callable, Awaitable

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.mqtt import async_subscribe
from homeassistant.components.mqtt.models import ReceiveMessage, MqttValueTemplate

from .const import DOMAIN, CONF_INPUTS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the KinCony KC868 binary sensors."""
    device_type = config_entry.data["device_type"]
    device_id = config_entry.data["device_id"]
    
    # Get the stored configuration
    config = hass.data[DOMAIN][config_entry.entry_id]
    input_keys = config[CONF_INPUTS]
    
    if not input_keys:
        _LOGGER.error("No input keys found in configuration")
        return
    
    # Create binary sensors for each input
    entities = []
    for input_key in input_keys:
        input_num = int(input_key.replace("input", ""))
        entities.append(
            KinconyBinarySensor(
                hass,
                device_type,
                device_id,
                input_key,
                f"Input {input_num}",
            )
        )
    
    async_add_entities(entities)

class KinconyBinarySensor(BinarySensorEntity):
    """Representation of a KinCony KC868 binary sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_type: str,
        device_id: str,
        input_id: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        self._hass = hass
        self._device_type = device_type
        self._device_id = device_id
        self._input_id = input_id
        self._name = name
        self._state = False
        self._unsubscribe: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await self._subscribe_mqtt()

    @property
    def name(self) -> str:
        """Return the name of the binary sensor."""
        return f"{self._device_type} {self._name}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"{self._device_type} {self._device_id}",
            manufacturer="KinCony",
            model=self._device_type,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._device_type}_{self._device_id}_{self._input_id}"

    async def _subscribe_mqtt(self) -> None:
        """Subscribe to MQTT topic."""
        topic = f"{self._device_type}/{self._device_id}/STATE"

        async def message_received(msg: ReceiveMessage) -> None:
            """Handle new MQTT messages."""
            try:
                payload = json.loads(msg.payload)
                if self._input_id in payload:
                    self._state = payload[self._input_id]["value"]
                    self.async_write_ha_state()
            except (json.JSONDecodeError, KeyError) as err:
                _LOGGER.error("Error processing message: %s", err)

        self._unsubscribe = await async_subscribe(
            self._hass,
            topic,
            message_received,
            qos=1,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from MQTT topic."""
        if self._unsubscribe:
            self._unsubscribe()
        