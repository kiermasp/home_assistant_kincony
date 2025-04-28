"""Constants for the Kincony KC868 integration."""
from homeassistant.const import Platform

DOMAIN = "kincony"
CONF_DEVICE_TYPE = "device_type"
CONF_DEVICE_ID = "device_id"
CONF_INPUTS = "inputs"
CONF_OUTPUTS = "outputs"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SWITCH] 