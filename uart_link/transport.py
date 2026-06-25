from __future__ import annotations

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
        return self._serial.write(data)

    def read(self, size: int = 1) -> bytes:
        if self._serial is None:
            raise TransportNotOpenError("transport is not open")
        return self._serial.read(size)

    @property
    def in_waiting(self) -> int:
        if self._serial is None:
            return 0
        return int(self._serial.in_waiting)
