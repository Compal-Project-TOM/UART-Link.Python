from __future__ import annotations

from dataclasses import dataclass

from .models import TrackpadPacket
from .type_ids import TrackpadRequestTypeId

REQUEST_PAYLOAD_LENGTHS: dict[int, int] = {
    int(TrackpadRequestTypeId.GET_DEVICE_ID): 0,
    int(TrackpadRequestTypeId.GET_INFORMATION): 0,
    int(TrackpadRequestTypeId.GET_FIRMWARE_VERSION): 0,
    int(TrackpadRequestTypeId.SET_SAMPLING_TIME): 4,
    int(TrackpadRequestTypeId.SET_ADC_GAIN): 3,
    int(TrackpadRequestTypeId.DO_CALIBRATION): 0,
    int(TrackpadRequestTypeId.RUN): 0,
    int(TrackpadRequestTypeId.STOP): 0,
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
    def __init__(self, adc: int, gain: int) -> None:
        if not (0 <= adc <= 0xFF):
            raise ValueError(f"adc must be in range [0, 255], got {adc}")
        if not (0 <= gain <= 0xFFFF):
            raise ValueError(f"gain must be in range [0, 65535], got {gain}")
        super().__init__(
            type_id=int(TrackpadRequestTypeId.SET_ADC_GAIN),
            payload=adc.to_bytes(1, "big") + gain.to_bytes(2, "big"),
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
