"""UART Link package for product-specific UART communication."""

from .client import MessageHandler, UartLinkClient
from .config import UartConfig
from .exceptions import ChecksumError, ProtocolError, TransportNotOpenError, UartLinkError
from .messages import (
    AdcGainMessage,
    AutoGainAttackThresholdMessage,
    AutoGainReleaseDelayFramesMessage,
    AutoGainReleaseThresholdMessage,
    CalibrationDataMessage,
    DeviceIdMessage,
    EffectiveActiveAreasMessage,
    SamplingTimeMessage,
    SamplingTooLongMessage,
    SensorFrameChunkMessage,
    TrackpadMessage,
    UnknownTrackpadMessage,
)
from .models import TrackpadPacket
from .protocol import DefaultTrackpadProtocol, TrackpadProtocol
from .transport import SerialTransport
from .type_ids import TrackpadTypeId

__version__ = "0.2.0"

__all__ = [
    "UartLinkClient",
    "MessageHandler",
    "UartConfig",
    "SerialTransport",
    "TrackpadProtocol",
    "DefaultTrackpadProtocol",
    "TrackpadPacket",
    "TrackpadMessage",
    "UnknownTrackpadMessage",
    "DeviceIdMessage",
    "EffectiveActiveAreasMessage",
    "CalibrationDataMessage",
    "SamplingTimeMessage",
    "SamplingTooLongMessage",
    "AdcGainMessage",
    "AutoGainAttackThresholdMessage",
    "AutoGainReleaseThresholdMessage",
    "AutoGainReleaseDelayFramesMessage",
    "SensorFrameChunkMessage",
    "TrackpadTypeId",
    "UartLinkError",
    "ProtocolError",
    "ChecksumError",
    "TransportNotOpenError",
]
