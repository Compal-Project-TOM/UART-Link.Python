# UART-Link.Python

Handle the communication between PC and Trackpad by UART

## Package framework

```text
uart_link/
  __init__.py         # public API export
  client.py           # send API + background receive thread + message callbacks
  messages.py         # typed message models + payload decoders
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
    SensorFrameChunkMessage,
    TrackpadTypeId,
    UartConfig,
    SerialTransport,
    UartLinkClient,
)
import time

cfg = UartConfig(port="COM3", baudrate=3000000)
transport = SerialTransport(cfg)
client = UartLinkClient(transport)


def on_message(message):
    print(f"{type(message).__name__}: type_id=0x{message.type_id:02X}")
    if isinstance(message, SensorFrameChunkMessage):
        print(message.sensor_values)


client.register_message_handler(on_message)
client.open()
try:
    # A background thread keeps receiving UART data and calls on_message
    # whenever a full packet is parsed and decoded.
    time.sleep(10)
finally:
    client.unregister_message_handler(on_message)
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

This default implementation currently focuses on **RX parsing only**
(Control Board -> PC). TX format (PC -> Control Board) is intentionally
reserved for a later update.

If your product uses another frame format, create your own class inheriting
`TrackpadProtocol` and inject it into `UartLinkClient`.

## Changelog

### 0.2.0 (2024-06-20)

- Add `TrackpadMessage` message feature. Now user can register a callback to receive different types of messages, Not
  `TrackpadPacket`.

### 0.1.0 (2024-06-20)

- Initial release