from dataclasses import dataclass


@dataclass(slots=True)
class UartConfig:
    port: str
    baudrate: int = 3000000
    timeout: float = 0.2
    write_timeout: float = 0.2
