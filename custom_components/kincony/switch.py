"""The Kincony KC868 switch platform."""
from __future__ import annotations

import logging
import json
from typing import Any, Callable, Awaitable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.mqtt import async_subscribe, async_publish
from homeassistant.components.mqtt.models import ReceiveMessage, MqttValueTemplate

from .const import DOMAIN, CONF_OUTPUTS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Kincony KC868 switches."""
    device_type = config_entry.data["device_type"]
    device_id = config_entry.data["device_id"]
    
    # Get the stored configuration
    config = hass.data[DOMAIN][config_entry.entry_id]
    output_keys = config[CONF_OUTPUTS]
    
    if not output_keys:
        _LOGGER.error("No output keys found in configuration")
        return
    
    # Create switches for each output
    entities = []
    for output_key in output_keys:
        output_num = int(output_key.replace("output", ""))
        entities.append(
            KinconySwitch(
                hass,
                device_type,
                device_id,
                output_key,
                f"Output {output_num}",
            )
        )
    
    async_add_entities(entities)

class KinconySwitch(SwitchEntity):
    """Representation of a Kincony KC868 switch."""

    def __init__(
        self,
        hass: HomeAssistant,
        device_type: str,
        device_id: str,
        output_id: str,
        name: str,
    ) -> None:
        """Initialize the switch."""
        self._hass = hass
        self._device_type = device_type
        self._device_id = device_id
        self._output_id = output_id
        self._name = name
        self._state = False
        self._unsubscribe = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to MQTT events."""
        await self._subscribe_mqtt()

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return f"{self._device_type} {self._name}"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._state

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=f"{self._device_type} {self._device_id}",
            manufacturer="Kincony",
            model=self._device_type,
        )

    async def _subscribe_mqtt(self) -> None:
        """Subscribe to MQTT topic."""
        topic = f"{self._device_type}/{self._device_id}/STATE"

        async def message_received(msg: ReceiveMessage) -> None:
            """Handle new MQTT messages."""
            try:
                payload = json.loads(msg.payload)
                if self._output_id in payload:
                    self._state = payload[self._output_id]["value"]
                    self.async_write_ha_state()
            except (json.JSONDecodeError, KeyError) as err:
                _LOGGER.error("Error processing message: %s", err)

        self._unsubscribe = await async_subscribe(
            self._hass,
            topic,
            message_received,
            qos=1,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._publish_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._publish_state(False)

    async def _publish_state(self, state: bool) -> None:
        """Publish the new state to MQTT."""
        topic = f"{self._device_type}/{self._device_id}/SET"
        payload = {self._output_id: {"value": state}}
        
        await async_publish(
            self._hass,
            topic,
            json.dumps(payload),
            retain=True,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Clean up when entity is removed."""
        if self._unsubscribe:
            unsubscribe = self._unsubscribe
            self._unsubscribe = None
            await unsubscribe() 