"""UART Link package for product-specific UART communication."""

from .client import ResponseHandler, UartLinkClient
from .config import UartConfig
from .exceptions import ChecksumError, ProtocolError, TransportNotOpenError, UartLinkError
from .response import (
    AdcGainResponse,
    AiInferenceTimeResponse,
    AiTouchFinger,
    AiTouchResultResponse,
    AutoGainAttackThresholdResponse,
    AutoGainReleaseDelayFramesResponse,
    AutoGainReleaseThresholdResponse,
    CalibrationDataResponse,
    DeviceIdResponse,
    EffectiveActiveAreasResponse,
    ReportModeResponse,
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
    GetAiInferenceTimeRequest,
    GetDeviceIdRequest,
    GetFirmwareVersionRequest,
    GetInformationRequest,
    RunRequest,
    SetAdcGainRequest,
    SetReportModeRequest,
    SetSamplingTimeRequest,
    StopRequest,
    TrackpadRequest,
)
from .transport import SerialTransport
from .type_ids import AdcGain, ReportMode, TrackpadRequestTypeId, TrackpadResponseTypeId

__version__ = "0.5.0"

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
    "AdcGain",
    "SetReportModeRequest",
    "DoCalibrationRequest",
    "RunRequest",
    "StopRequest",
    "GetAiInferenceTimeRequest",
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
    "ReportModeResponse",
    "SensorFrameChunkResponse",
    "AiTouchFinger",
    "AiTouchResultResponse",
    "AiInferenceTimeResponse",
    "TrackpadResponseTypeId",
    "TrackpadRequestTypeId",
    "ReportMode",
    "FirmwareVersionResponse",
    "CommandNotSupportedResponse",
    "UartLinkError",
    "ProtocolError",
    "ChecksumError",
    "TransportNotOpenError",
]
