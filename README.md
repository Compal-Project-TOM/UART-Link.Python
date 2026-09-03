# UART-Link.Python

Handle the communication between PC and Trackpad by UART

## Package framework

```text
uart_link/
  __init__.py         # public API export
  client.py           # send API + background receive thread + response callbacks
  response.py         # typed response models + payload decoders
  request.py          # typed request models + payload encoders
  config.py           # UART config dataclass
  transport.py        # pyserial transport wrapper
  models.py           # packet model
  protocol.py         # protocol interface + default framing implementation
  exceptions.py       # package exception hierarchy
```

## Install (editable)

```bash
pip install -e .
```

## Quick start

```python
from uart_link import (
  GetDeviceIdRequest,
  RunRequest,
  SensorFrameChunkResponse,
  UartConfig,
  SerialTransport,
  UartLinkClient,
)
import time

cfg = UartConfig(port="COM3", baudrate=3000000)
transport = SerialTransport(cfg)
client = UartLinkClient(transport)


def on_response(resp):
  print(f"{type(resp).__name__}: type_id=0x{resp.type_id:02X}")
  if isinstance(resp, SensorFrameChunkResponse):
    print(resp.sensor_values)


client.register_response_handler(on_response)
client.open()
try:
  client.send_request(GetDeviceIdRequest())
  client.send_request(RunRequest())

  # A background thread keeps receiving UART data and calls on_response
  # whenever a full packet is parsed and decoded.
  time.sleep(10)
finally:
  client.unregister_response_handler(on_response)
  client.close()
```

`open()` will start an internal background receive thread automatically.

## Example

Run:

```bash
py examples\read_uart.py --port COM3 --baudrate 3000000
```

## Product protocol customization

Current default frame in `DefaultTrackpadProtocol`:
`MAGIC(2: 0x55 0xAA) | TYPE_ID(1) | PAYLOAD_LEN(2) | PAYLOAD(N)`
for both RX (Control Board -> PC) and TX (PC -> Control Board).

If your product uses another frame format, create your own class inheriting
`TrackpadProtocol` and inject it into `UartLinkClient`.

## Changelog

### 0.3.2 (2026-09-03)
- Fix `DeviceIdResponse` payload decoding issue
- Fix `FirmwareVersionResponse` payload decoding issue

### 0.3.1 (2024-07-07)
- Fix pyproject.toml version mismatch issue

### 0.3.0 (2024-07-01)
- Add `TrackpadRequest` for sending request messages
- Rename `TrackpadMessage` to `TrackpadResponse` for receiving response messages

### 0.2.0 (2024-06-20)

- Add `TrackpadMessage` message feature. Now user can register a callback to receive different types of messages, Not
  `TrackpadPacket`.

### 0.1.0 (2024-06-20)

- Initial release