from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import TrackpadPacket


class TrackpadProtocol(ABC):
    @abstractmethod
    def encode(self, packet: TrackpadPacket) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decode_from_buffer(self, buffer: bytearray) -> Iterable[TrackpadPacket]:
        raise NotImplementedError


class DefaultTrackpadProtocol(TrackpadProtocol):
    """
    RX frame format (Control Board -> PC):
      MAGIC(2) | TYPE_ID(1) | PAYLOAD_LEN(2) | PAYLOAD(N)
    """

    MAGIC = b"\x55\xAA"
    HEADER_SIZE = 2 + 1 + 2

    def encode(self, packet: TrackpadPacket) -> bytes:
        raise NotImplementedError(
            "TX format (PC -> Control Board) is reserved and not implemented yet."
        )

    def decode_from_buffer(self, buffer: bytearray) -> Iterable[TrackpadPacket]:
        packets: list[TrackpadPacket] = []

        while True:
            magic_index = buffer.find(self.MAGIC)
            if magic_index < 0:
                buffer.clear()
                return packets

            if magic_index > 0:
                del buffer[:magic_index]

            if len(buffer) < self.HEADER_SIZE:
                return packets

            type_id = buffer[2]
            payload_len = int.from_bytes(buffer[3:5], "big")
            frame_size = self.HEADER_SIZE + payload_len
            if len(buffer) < frame_size:
                return packets

            packets.append(
                TrackpadPacket(
                    type_id=type_id,
                    payload=bytes(buffer[5:frame_size]),
                )
            )
            del buffer[:frame_size]
