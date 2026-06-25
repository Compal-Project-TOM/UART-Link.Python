from enum import IntEnum


class TrackpadTypeId(IntEnum):
    DEVICE_ID = 0x01
    """Trackpad device ID (payload length: 16 bytes)"""

    EFFECTIVE_ACTIVE_AREAS = 0x02
    """Effective active area (payload length: 2 bytes)"""

    CALIBRATION_DATA = 0x10
    """Calibration data (2 bytes per sensor, max 65530 bytes)"""

    SAMPLING_TIME = 0x20
    """Sampling time (payload length: 4 bytes)"""

    ADC_GAIN = 0x21
    """ADC gain (payload length: 2 bytes)"""

    AUTO_GAIN_ATTACK_THD = 0x22
    """(Optional) Auto-gain attack threshold (payload length: 4 bytes)"""

    AUTO_GAIN_RELEASE_THD = 0x23
    """(Optional) Auto gain release threshold (payload length: 4 bytes)"""

    AUTO_GAIN_RELEASE_DELAY_FRAMES = 0x24
    """(Optional) Auto gain release delay frames (payload length: 4 bytes)"""

    SENSOR_FRAME_CHUNK = 0x30
    """Sensor frame chunk (2 bytes per sensor, max 65530 bytes)"""

    SAMPLING_TOO_LONG = 0xE0
    """Sampling too long (payload length: 0 bytes)"""
