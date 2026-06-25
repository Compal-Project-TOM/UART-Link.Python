from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import TrackpadPacket
from .type_ids import TrackpadTypeId


@dataclass(slots=True)
class TrackpadMessage:
    """
    Base class for all trackpad messages
    """
    packet: TrackpadPacket

    @property
    def type_id(self) -> int:
        return self.packet.type_id

    @property
    def payload(self) -> bytes:
        return self.packet.payload


@dataclass(slots=True)
class UnknownTrackpadMessage(TrackpadMessage):
    """
    Unknown trackpad message
    """
    pass


@dataclass(slots=True)
class DeviceIdMessage(TrackpadMessage):
    """
    DeviceId message
    """
    device_id: bytes

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "DeviceIdMessage":
        if len(packet.payload) != 16:
            raise ValueError("device id payload must be 16 bytes")
        return cls(packet=packet, device_id=packet.payload)


@dataclass(slots=True)
class EffectiveActiveAreasMessage(TrackpadMessage):
    """
    Effective active areas message
    """
    active_area_count: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "EffectiveActiveAreasMessage":
        if len(packet.payload) != 2:
            raise ValueError("effective active areas payload must be 2 bytes")
        return cls(packet=packet, active_area_count=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class SamplingTimeMessage(TrackpadMessage):
    """
    Sampling time message
    """
    sampling_time_us: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SamplingTimeMessage":
        if len(packet.payload) != 4:
            raise ValueError("sampling time payload must be 4 bytes")
        return cls(packet=packet, sampling_time_us=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AdcGainMessage(TrackpadMessage):
    """
    ADC gain message
    """
    gain: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AdcGainMessage":
        if len(packet.payload) != 2:
            raise ValueError("ADC gain payload must be 2 bytes")
        return cls(packet=packet, gain=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AutoGainAttackThresholdMessage(TrackpadMessage):
    """
    Auto Gain Attack Threshold message
    """
    threshold: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AutoGainAttackThresholdMessage":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain attack threshold payload must be 4 bytes")
        return cls(packet=packet, threshold=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AutoGainReleaseThresholdMessage(TrackpadMessage):
    """
    Auto Gain Release Threshold message
    """
    threshold: int

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "AutoGainReleaseThresholdMessage":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain release threshold payload must be 4 bytes")
        return cls(packet=packet, threshold=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class AutoGainReleaseDelayFramesMessage(TrackpadMessage):
    """
    Auto Gain Release Delay Frames message
    """
    delay_frames: int

    @classmethod
    def from_packet(
            cls, packet: TrackpadPacket
    ) -> "AutoGainReleaseDelayFramesMessage":
        if len(packet.payload) != 4:
            raise ValueError("auto-gain release delay frames payload must be 4 bytes")
        return cls(packet=packet, delay_frames=int.from_bytes(packet.payload, "big"))


@dataclass(slots=True)
class CalibrationDataMessage(TrackpadMessage):
    """
    Calibration data message
    """
    sensor_values: tuple[int, ...]

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "CalibrationDataMessage":
        return cls(packet=packet, sensor_values=_decode_u16_values(packet.payload))


@dataclass(slots=True)
class SensorFrameChunkMessage(TrackpadMessage):
    """
    Sensor Frame Chunk message
    """
    sensor_values: tuple[int, ...]

    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SensorFrameChunkMessage":
        return cls(packet=packet, sensor_values=_decode_u16_values(packet.payload))


@dataclass(slots=True)
class SamplingTooLongMessage(TrackpadMessage):
    """
    Sampling Too Long message
    """
    @classmethod
    def from_packet(cls, packet: TrackpadPacket) -> "SamplingTooLongMessage":
        if packet.payload:
            raise ValueError("sampling too long payload must be empty")
        return cls(packet=packet)


def default_trackpad_message_decoder(packet: TrackpadPacket) -> TrackpadMessage:
    decoder = _DEFAULT_MESSAGE_DECODERS.get(packet.type_id)
    if decoder is None:
        return UnknownTrackpadMessage(packet)
    return decoder(packet)


def _decode_u16_values(payload: bytes) -> tuple[int, ...]:
    if len(payload) % 2 != 0:
        raise ValueError("payload length must be an even number of bytes")
    return tuple(
        int.from_bytes(payload[index: index + 2], "big")
        for index in range(0, len(payload), 2)
    )


TrackpadMessageDecoder = Callable[[TrackpadPacket], TrackpadMessage]

_DEFAULT_MESSAGE_DECODERS: dict[int, TrackpadMessageDecoder] = {
    int(TrackpadTypeId.DEVICE_ID): DeviceIdMessage.from_packet,
    int(TrackpadTypeId.EFFECTIVE_ACTIVE_AREAS): EffectiveActiveAreasMessage.from_packet,
    int(TrackpadTypeId.CALIBRATION_DATA): CalibrationDataMessage.from_packet,
    int(TrackpadTypeId.SAMPLING_TIME): SamplingTimeMessage.from_packet,
    int(TrackpadTypeId.ADC_GAIN): AdcGainMessage.from_packet,
    int(TrackpadTypeId.AUTO_GAIN_ATTACK_THD): AutoGainAttackThresholdMessage.from_packet,
    int(TrackpadTypeId.AUTO_GAIN_RELEASE_THD): AutoGainReleaseThresholdMessage.from_packet,
    int(TrackpadTypeId.AUTO_GAIN_RELEASE_DELAY_FRAMES): AutoGainReleaseDelayFramesMessage.from_packet,
    int(TrackpadTypeId.SENSOR_FRAME_CHUNK): SensorFrameChunkMessage.from_packet,
    int(TrackpadTypeId.SAMPLING_TOO_LONG): SamplingTooLongMessage.from_packet,
}
