from __future__ import annotations

import time
from typing import Optional

import serial

from .config import UartConfig
from .exceptions import TransportNotOpenError


class SerialTransport:
    def __init__(self, config: UartConfig) -> None:
        self._config = config
        self._serial: Optional[serial.Serial] = None

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def open(self) -> None:
        if self.is_open:
            return
        self._serial = serial.Serial(
            port=self._config.port,
            baudrate=self._config.baudrate,
            timeout=self._config.timeout,
            write_timeout=self._config.write_timeout,
        )

    def close(self) -> None:
        if self._serial is None:
            return
        self._serial.close()
        self._serial = None

    def write(self, data: bytes) -> int | None:
        if self._serial is None:
            raise TransportNotOpenError("transport is not open")

        # FIXME: Trackpad上不知道為什麼只能收到2個Bytes，先用迴圈一個個Byte送，之後再找原因
        # return self._serial.write(data)

        for b in data:
            self._serial.write(b.to_bytes(1, byteorder="big"))
            time.sleep(0.0001)  # 100us delay between bytes
        return len(data)

    def read(self, size: int = 1) -> bytes:
        if self._serial is None:
            raise TransportNotOpenError("transport is not open")
        return self._serial.read(size)

    @property
    def in_waiting(self) -> int:
        if self._serial is None:
            return 0
        return int(self._serial.in_waiting)
