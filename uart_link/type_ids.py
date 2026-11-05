from enum import IntEnum, IntFlag


class TrackpadRequestTypeId(IntEnum):
    GET_DEVICE_ID = 0x01
    """Get device id (payload length: 0 byte)"""

    GET_INFORMATION = 0x02
    """Get device information (payload length: 0 byte)"""

    GET_FIRMWARE_VERSION = 0x03
    """Get firmware version (payload length: 0 byte)"""

    SET_SAMPLING_TIME = 0x10
    """Set sampling time (payload length: 4 bytes)"""

    SET_ADC_GAIN = 0x11
    """Set adc gain (payload length: 3 bytes)"""

    SET_REPORT_MODE = 0x12
    """Set which data to report while running (payload length: 1 byte)"""

    DO_CALIBRATION = 0x20
    """Do calibration (payload length: 0 byte)"""

    RUN = 0x21
    """Run (payload length: 0 byte)"""

    STOP = 0x22
    """Stop (payload length: 0 byte)"""

    GET_AI_INFERENCE_TIME = 0x72
    """Get AI inference time (payload length: 0 byte)"""


class TrackpadResponseTypeId(IntEnum):
    DEVICE_ID = 0x81
    """Trackpad device ID (payload length: 16 bytes)"""

    EFFECTIVE_ACTIVE_AREAS = 0x82
    """Effective active area (payload length: 2 bytes)"""

    FIRMWARE_VERSION = 0x83
    """Firmware version (payload length: 128 bytes)"""

    CALIBRATION_DATA = 0x90
    """Calibration data (2 bytes per sensor, max 65530 bytes)"""

    SAMPLING_TIME = 0xA0
    """Sampling time (payload length: 4 bytes)"""

    ADC_GAIN = 0xA1
    """ADC gain (payload length: 3 bytes)"""

    AUTO_GAIN_ATTACK_THD = 0xA2
    """(Optional) Auto-gain attack threshold (payload length: 4 bytes)"""

    AUTO_GAIN_RELEASE_THD = 0xA3
    """(Optional) Auto gain release threshold (payload length: 4 bytes)"""

    AUTO_GAIN_RELEASE_DELAY_FRAMES = 0xA4
    """(Optional) Auto gain release delay frames (payload length: 4 bytes)"""

    REPORT_MODE = 0xA5
    """Report mode (payload length: 1 byte)"""

    SENSOR_FRAME_CHUNK = 0xB0
    """Sensor frame chunk (2 bytes per sensor, max 65530 bytes)"""

    AI_TOUCH_RESULT = 0xB1
    """AI touch result (payload length: 6 + 7N bytes, N = 0 ~ 5)"""

    SAMPLING_TOO_LONG = 0xE0
    """Sampling too long (payload length: 0 byte)"""

    COMMAND_NOT_SUPPORTED = 0xE1
    """Command not supported (payload length: 0 byte)"""

    AI_INFERENCE_TIME = 0xF2
    """AI inference time (payload length: 20 bytes)"""


class ReportMode(IntFlag):
    """Bits of Set Report Mode (0x12) and Report Mode (0xA5)."""

    NONE = 0x00

    SENSOR_FRAME_CHUNK = 0x01
    """Report Sensor Frame Chunk (0xB0) while running"""

    AI_TOUCH_RESULT = 0x02
    """Report AI Touch Result (0xB1) while running"""
