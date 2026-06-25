from dataclasses import dataclass


@dataclass(slots=True)
class TrackpadPacket:
    type_id: int
    payload: bytes = b""
