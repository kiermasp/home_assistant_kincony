# Home Assistant KinCony KC868 Integration

This is a custom component for Home Assistant that integrates KinCony KC868 devices via MQTT.

## Features

- Supports up to 64 binary inputs
- Supports up to 64 switch outputs
- Real-time state updates via MQTT
- Automatic device discovery
- Configurable device type and ID

## Installation

1. Install this custom component using HACS:

   - Add this repository to HACS
   - Search for "KinCony KC868" in the HACS store
   - Click Install

2. Restart Home Assistant

## Configuration

1. In Home Assistant, go to Configuration > Integrations
2. Click the "+ Add Integration" button
3. Search for "KinCony KC868"
4. Enter the following information:
   - Device Type: The type of your KinCony device (e.g., "KC868_A64")
   - Device ID: The unique ID of your device (e.g., "D4D4DAE11EA4")

## MQTT Topics

The integration uses the following MQTT topics:

- State topic: `{device_type}/{device_id}/STATE`
- Set topic: `{device_type}/{device_id}/SET`

## State Format

The state topic publishes a JSON payload with the following structure:

```json
{
  "input1": {"value": false},
  "input2": {"value": false},
  ...
  "output1": {"value": false},
  "output2": {"value": false},
  ...
  "adc1": {"value": 0},
  "adc2": {"value": 0},
  "adc3": {"value": 0},
  "adc4": {"value": 0}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
