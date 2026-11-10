from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable, ClassVar

from .models import TrackpadPacket
from .type_ids import ReportMode, TrackpadResponseTypeId


@dataclass(slots=True)
class TrackpadResponse:
    """
    Base class for all trackpad responses
    """
    packet: TrackpadPacket

    @property
    def type_id(self) -> int:
        return self.packet.type_id

    @property
    def payload(self) -> bytes:
        return self.packet.payload


@dataclass(slots=True)
class UnknownTrackpadResponse(TrackpadResponse):
    """
    Unknown trackpad response
    """
    pass


@dataclass(slots=True)
class DeviceIdResponse(TrackpadResponse):
    """
    DeviceId response
    """
    device_id: str

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "DeviceIdResponse":
        if len(packet.payload) != 16:
            raise ValueError("device id payload must be 16 bytes")
        device_id = packet.payload.split(b"\x00", 1)[0].decode("ascii", errors="ignore")
        return cls(packet=packet, device_id=device_id)


@dataclass(slots=True)
class EffectiveActiveAreasResponse(TrackpadResponse):
    """
    Effective active areas response
    """
    active_area_count: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "EffectiveActiveAreasResponse":
        if len(packet.payload) != 2:
            raise ValueError("effective active areas payload must be 2 bytes")
        return cls(packet=packet, active_area_count=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class FirmwareVersionResponse(TrackpadResponse):
    """
    Firmware version response
    """
    firmware_version: str

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "FirmwareVersionResponse":
        if len(packet.payload) != 128:
            raise ValueError("firmware version payload must be 128 bytes")
        firmware_version = packet.payload.split(b"\x00", 1)[0].decode("ascii", errors="ignore")
        return cls(packet=packet, firmware_version=firmware_version)


@dataclass(slots=True)
class SamplingTimeResponse(TrackpadResponse):
    """
    Sampling time response
    """
    sampling_time_us: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SamplingTimeResponse":
        if len(packet.payload) != 4:
            raise ValueError("sampling time payload must be 4 bytes")
        return cls(packet=packet, sampling_time_us=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AdcGainResponse(TrackpadResponse):
    """
    ADC gain response
    """
    adc: int
    gain: int
    """AdcGain code (0b000 ~ 0b111)"""

    @property
    def gain_multiplier(self) -> int:
        """Actual gain value, e.g. code 0b011 -> 8"""
        return 1 << self.gain

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AdcGainResponse":
        if len(packet.payload) != 3:
            raise ValueError("ADC gain payload must be 3 bytes")
        adc = packet.payload[0]
        gain = int.from_bytes(packet.payload[1:3], "big")
        return cls(packet=packet, adc=adc, gain=gain)


@dataclass(slots=True)
class AutoGainAttackThresholdResponse(TrackpadResponse):
    """
    Auto Gain Attack Threshold response
    """
    threshold: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AutoGainAttackThresholdResponse":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain attack threshold payload must be 4 bytes")
        return cls(packet=packet, threshold=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AutoGainReleaseThresholdResponse(TrackpadResponse):
    """
    Auto Gain Release Threshold response
    """
    threshold: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AutoGainReleaseThresholdResponse":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain release threshold payload must be 4 bytes")
        return cls(packet=packet, threshold=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AutoGainReleaseDelayFramesResponse(TrackpadResponse):
    """
    Auto Gain Release Delay Frames response
    """
    delay_frames: int

    @classmethod
    def from_packet(
            cls, packet: TrackpadPacket
    ) -> "AutoGainReleaseDelayFramesResponse":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain release delay frames payload must be 4 bytes")
        return cls(packet=packet, delay_frames=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class CalibrationDataResponse(TrackpadResponse):
    """
    Calibration data response
    """
    sensor_values: tuple[int, ...]

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "CalibrationDataResponse":
        return cls(packet=packet, sensor_values=_decode_u16_values(packet.payload))


@dataclass(slots=True)
class SensorFrameChunkResponse(TrackpadResponse):
    """
    Sensor Frame Chunk response
    """
    sensor_values: tuple[int, ...]

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SensorFrameChunkResponse":
        return cls(packet=packet, sensor_values=_decode_u16_values(packet.payload))


@dataclass(slots=True)
class SamplingTooLongResponse(TrackpadResponse):
    """
    Sampling Too Long response
    """

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SamplingTooLongResponse":
        if packet.payload:
            raise ValueError("sampling too long payload must be empty")
        return cls(packet=packet)


@dataclass(slots=True)
class CommandNotSupportedResponse(TrackpadResponse):
    """
    Command Not Supported response
    """

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "CommandNotSupportedResponse":
        if packet.payload:
            raise ValueError("command not supported payload must be empty")
        return cls(packet=packet)


@dataclass(slots=True)
class ReportModeResponse(TrackpadResponse):
    """
    Report mode response: which data the device reports while running
    """
    mode: ReportMode

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "ReportModeResponse":
        if len(packet.payload) != 1:
            raise ValueError("report mode payload must be 1 byte")
        return cls(packet=packet, mode=ReportMode(packet.payload[0]))


@dataclass(slots=True, frozen=True)
class AiTouchFinger:
    """
    One finger entry in AI Touch Result (7 bytes)
    """
    contact_id: int
    state: int
    x: int
    """X in 0.01 mm"""
    y: int
    """Y in 0.01 mm"""
    confidence: int
    """0 ~ 255, maps to 0.0 ~ 1.0"""

    SIZE: ClassVar[int] = 7

    @property
    def active(self) -> bool:
        return bool(self.state & 0x01)

    @property
    def just_lifted(self) -> bool:
        return bool(self.state & 0x02)

    @property
    def x_mm(self) -> float:
        return self.x / 100

    @property
    def y_mm(self) -> float:
        return self.y / 100

    @property
    def confidence_ratio(self) -> float:
        return self.confidence / 255


@dataclass(slots=True)
class AiTouchResultResponse(TrackpadResponse):
    """
    AI touch result response, sent after each AI inference
    """
    frame_index: int
    flags: int
    fingers: tuple[AiTouchFinger, ...]

    HEADER_SIZE: ClassVar[int] = 6

    @property
    def baseline_ready(self) -> bool:
        return bool(self.flags & 0x01)

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AiTouchResultResponse":
        payload = packet.payload
        if len(payload) < cls.HEADER_SIZE:
            raise ValueError(f"AI touch result payload must be at least {cls.HEADER_SIZE} bytes")
        frame_index, flags, finger_count = struct.unpack_from(">IBB", payload, 0)
        expected = cls.HEADER_SIZE + finger_count * AiTouchFinger.SIZE
        if len(payload) != expected:
            raise ValueError(
                f"AI touch result with {finger_count} fingers must be {expected} bytes, "
                f"got {len(payload)} bytes"
            )
        fingers = tuple(
            AiTouchFinger(*struct.unpack_from(">BBHHB", payload, cls.HEADER_SIZE + i * AiTouchFinger.SIZE))
            for i in range(finger_count)
        )
        return cls(packet=packet, frame_index=frame_index, flags=flags, fingers=fingers)


@dataclass(slots=True)
class AiInferenceTimeResponse(TrackpadResponse):
    """
    AI inference time response, all times in us
    """
    frame_index: int
    total_us: int
    model_us: int
    pre_us: int
    post_us: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AiInferenceTimeResponse":
        if len(packet.payload) != 20:
            raise ValueError("AI inference time payload must be 20 bytes")
        frame_index, total_us, model_us, pre_us, post_us = struct.unpack(">5I", packet.payload)
        return cls(
            packet=packet,
            frame_index=frame_index,
            total_us=total_us,
            model_us=model_us,
            pre_us=pre_us,
            post_us=post_us,
        )


def default_trackpad_response_decoder(packet: TrackpadPacket) -> TrackpadResponse:
    decoder = _DEFAULT_RESPONSE_DECODERS.get(packet.type_id)
    if decoder is None:
        return UnknownTrackpadResponse(packet)
    return decoder(packet)


def _decode_u16_values(payload: bytes) -> tuple[int, ...]:
    if len(payload) % 2 != 0:
        raise ValueError("payload length must be an even number of bytes")
    return tuple(
        int.from_bytes(payload[index: index + 2], "big")
        for index in range(0, len(payload), 2)
    )


TrackpadResponseDecoder = Callable[[TrackpadPacket], TrackpadResponse]

_DEFAULT_RESPONSE_DECODERS: dict[int, TrackpadResponseDecoder] = {
    int(TrackpadResponseTypeId.DEVICE_ID): DeviceIdResponse.from_packet,
    int(TrackpadResponseTypeId.EFFECTIVE_ACTIVE_AREAS): EffectiveActiveAreasResponse.from_packet,
    int(TrackpadResponseTypeId.FIRMWARE_VERSION): FirmwareVersionResponse.from_packet,
    int(TrackpadResponseTypeId.CALIBRATION_DATA): CalibrationDataResponse.from_packet,
    int(TrackpadResponseTypeId.SAMPLING_TIME): SamplingTimeResponse.from_packet,
    int(TrackpadResponseTypeId.ADC_GAIN): AdcGainResponse.from_packet,
    int(TrackpadResponseTypeId.AUTO_GAIN_ATTACK_THD): AutoGainAttackThresholdResponse.from_packet,
    int(TrackpadResponseTypeId.AUTO_GAIN_RELEASE_THD): AutoGainReleaseThresholdResponse.from_packet,
    int(TrackpadResponseTypeId.AUTO_GAIN_RELEASE_DELAY_FRAMES): AutoGainReleaseDelayFramesResponse.from_packet,
    int(TrackpadResponseTypeId.REPORT_MODE): ReportModeResponse.from_packet,
    int(TrackpadResponseTypeId.SENSOR_FRAME_CHUNK): SensorFrameChunkResponse.from_packet,
    int(TrackpadResponseTypeId.AI_TOUCH_RESULT): AiTouchResultResponse.from_packet,
    int(TrackpadResponseTypeId.SAMPLING_TOO_LONG): SamplingTooLongResponse.from_packet,
    int(TrackpadResponseTypeId.COMMAND_NOT_SUPPORTED): CommandNotSupportedResponse.from_packet,
    int(TrackpadResponseTypeId.AI_INFERENCE_TIME): AiInferenceTimeResponse.from_packet,
}
