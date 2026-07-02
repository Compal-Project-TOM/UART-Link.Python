from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import TrackpadPacket
from .type_ids import TrackpadResponseTypeId


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
        return cls(packet=packet, device_id=packet.payload.hex())


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
        return cls(packet=packet, firmware_version=packet.payload.hex())


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
    int(TrackpadResponseTypeId.SENSOR_FRAME_CHUNK): SensorFrameChunkResponse.from_packet,
    int(TrackpadResponseTypeId.SAMPLING_TOO_LONG): SamplingTooLongResponse.from_packet,
    int(TrackpadResponseTypeId.COMMAND_NOT_SUPPORTED): CommandNotSupportedResponse.from_packet,
}
