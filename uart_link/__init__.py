"""UART Link package for product-specific UART communication."""

from .client import PacketHandler, UartLinkClient
from .config import UartConfig
from .exceptions import ChecksumError, ProtocolError, TransportNotOpenError, UartLinkError
from .models import TrackpadPacket
from .protocol import DefaultTrackpadProtocol, TrackpadProtocol
from .transport import SerialTransport
from .type_ids import TrackpadTypeId

__version__ = "0.1.0"

__all__ = [
    "UartLinkClient",
    "PacketHandler",
    "UartConfig",
    "SerialTransport",
    "TrackpadProtocol",
    "DefaultTrackpadProtocol",
    "TrackpadPacket",
    "TrackpadTypeId",
    "UartLinkError",
    "ProtocolError",
    "ChecksumError",
    "TransportNotOpenError",
]