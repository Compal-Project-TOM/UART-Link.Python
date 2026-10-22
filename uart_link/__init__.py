"""UART Link package for product-specific UART communication."""

from .client import ResponseHandler, UartLinkClient
from .config import UartConfig
from .exceptions import ChecksumError, ProtocolError, TransportNotOpenError, UartLinkError
from .response import (
    AdcGainResponse,
    AutoGainAttackThresholdResponse,
    AutoGainReleaseDelayFramesResponse,
    AutoGainReleaseThresholdResponse,
    CalibrationDataResponse,
    DeviceIdResponse,
    EffectiveActiveAreasResponse,
    SamplingTimeResponse,
    SamplingTooLongResponse,
    SensorFrameChunkResponse,
    TrackpadResponse,
    FirmwareVersionResponse,
    CommandNotSupportedResponse,
    UnknownTrackpadResponse,
)
from .models import TrackpadPacket
from .protocol import DefaultTrackpadProtocol, TrackpadProtocol
from .request import (
    DoCalibrationRequest,
    GetDeviceIdRequest,
    GetFirmwareVersionRequest,
    GetInformationRequest,
    RunRequest,
    SetAdcGainRequest,
    SetSamplingTimeRequest,
    StopRequest,
    TrackpadRequest,
)
from .transport import SerialTransport
from .type_ids import TrackpadRequestTypeId, TrackpadResponseTypeId

__version__ = "0.4.0"

__all__ = [
    "UartLinkClient",
    "ResponseHandler",
    "UartConfig",
    "SerialTransport",
    "TrackpadProtocol",
    "DefaultTrackpadProtocol",
    "TrackpadPacket",
    "TrackpadRequest",
    "GetDeviceIdRequest",
    "GetInformationRequest",
    "GetFirmwareVersionRequest",
    "SetSamplingTimeRequest",
    "SetAdcGainRequest",
    "DoCalibrationRequest",
    "RunRequest",
    "StopRequest",
    "TrackpadResponse",
    "UnknownTrackpadResponse",
    "DeviceIdResponse",
    "EffectiveActiveAreasResponse",
    "CalibrationDataResponse",
    "SamplingTimeResponse",
    "SamplingTooLongResponse",
    "AdcGainResponse",
    "AutoGainAttackThresholdResponse",
    "AutoGainReleaseThresholdResponse",
    "AutoGainReleaseDelayFramesResponse",
    "SensorFrameChunkResponse",
    "TrackpadResponseTypeId",
    "TrackpadRequestTypeId",
    "FirmwareVersionResponse",
    "CommandNotSupportedResponse",
    "UartLinkError",
    "ProtocolError",
    "ChecksumError",
    "TransportNotOpenError",
]
