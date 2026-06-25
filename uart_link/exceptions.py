class UartLinkError(Exception):
    """Base exception for this package."""


class TransportNotOpenError(UartLinkError):
    """Raised when I/O is attempted before opening the transport."""


class ProtocolError(UartLinkError):
    """Raised when frame parsing or validation fails."""


class ChecksumError(ProtocolError):
    """Raised when the checksum is invalid."""
