from __future__ import annotations

from dataclasses import dataclass

from .models import TrackpadPacket
from .type_ids import AdcGain, ReportMode, TrackpadRequestTypeId

REQUEST_PAYLOAD_LENGTHS: dict[int, int] = {
    int(TrackpadRequestTypeId.GET_DEVICE_ID): 0,
    int(TrackpadRequestTypeId.GET_INFORMATION): 0,
    int(TrackpadRequestTypeId.GET_FIRMWARE_VERSION): 0,
    int(TrackpadRequestTypeId.SET_SAMPLING_TIME): 4,
    int(TrackpadRequestTypeId.SET_ADC_GAIN): 3,
    int(TrackpadRequestTypeId.SET_REPORT_MODE): 1,
    int(TrackpadRequestTypeId.DO_CALIBRATION): 0,
    int(TrackpadRequestTypeId.RUN): 0,
    int(TrackpadRequestTypeId.STOP): 0,
    int(TrackpadRequestTypeId.GET_AI_INFERENCE_TIME): 0,
}


def validate_trackpad_request(type_id: int, payload: bytes) -> None:
    if not (0 <= type_id <= 0xFF):
        raise ValueError(f"type_id must be in range [0, 255], got {type_id}")
    expected_payload_length = REQUEST_PAYLOAD_LENGTHS.get(type_id)
    if expected_payload_length is not None and len(payload) != expected_payload_length:
        raise ValueError(
            f"type_id 0x{type_id:02X} payload must be {expected_payload_length} bytes, "
            f"got {len(payload)} bytes"
        )


@dataclass(slots=True)
class TrackpadRequest:
    type_id: int
    payload: bytes = b""

    def __post_init__(self) -> None:
        self.payload = bytes(self.payload)
        validate_trackpad_request(self.type_id, self.payload)

    def to_packet(self) -> TrackpadPacket:
        return TrackpadPacket(type_id=self.type_id, payload=self.payload)


class GetDeviceIdRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.GET_DEVICE_ID))


class GetInformationRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.GET_INFORMATION))


class GetFirmwareVersionRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.GET_FIRMWARE_VERSION))


class SetSamplingTimeRequest(TrackpadRequest):
    def __init__(self, sampling_time_us: int) -> None:
        if not (0 <= sampling_time_us <= 0xFFFFFFFF):
            raise ValueError(
                f"sampling_time_us must be in range [0, 4294967295], got {sampling_time_us}"
            )
        super().__init__(
            type_id=int(TrackpadRequestTypeId.SET_SAMPLING_TIME),
            payload=sampling_time_us.to_bytes(4, "big"),
        )


class SetAdcGainRequest(TrackpadRequest):
    """設定 ADC 增益，gain 只能是 AdcGain 代碼 (GAIN_1 = 0b000 ~ GAIN_128 = 0b111)。"""

    def __init__(self, adc: int, gain: AdcGain | int) -> None:
        if not (0 <= adc <= 0xFF):
            raise ValueError(f"adc must be in range [0, 255], got {adc}")
        if type(gain) is not AdcGain and type(gain) is not int:
            raise ValueError(f"gain must be an AdcGain code, got {gain!r}")
        try:
            code = AdcGain(gain)
        except ValueError:
            raise ValueError(
                f"gain must be an AdcGain code in range [0, 7], got {gain!r}"
            ) from None
        super().__init__(
            type_id=int(TrackpadRequestTypeId.SET_ADC_GAIN),
            payload=adc.to_bytes(1, "big") + int(code).to_bytes(2, "big"),
        )


class SetReportModeRequest(TrackpadRequest):
    """選擇 Run 時要回報哪些資料，例如 ReportMode.SENSOR_FRAME_CHUNK | ReportMode.AI_TOUCH_RESULT。"""

    def __init__(self, mode: ReportMode | int) -> None:
        mode_value = int(mode)
        if not (0 <= mode_value <= 0xFF):
            raise ValueError(f"mode must be in range [0, 255], got {mode_value}")
        super().__init__(
            type_id=int(TrackpadRequestTypeId.SET_REPORT_MODE),
            payload=mode_value.to_bytes(1, "big"),
        )


class DoCalibrationRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.DO_CALIBRATION))


class RunRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.RUN))


class StopRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.STOP))


class GetAiInferenceTimeRequest(TrackpadRequest):
    def __init__(self) -> None:
        super().__init__(type_id=int(TrackpadRequestTypeId.GET_AI_INFERENCE_TIME))
