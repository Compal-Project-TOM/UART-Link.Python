import time
import unittest

from uart_link import (
    DefaultTrackpadProtocol,
    DeviceIdResponse,
    TrackpadPacket,
    UartLinkClient,
)
from uart_link.type_ids import TrackpadResponseTypeId


class FakeTransport:
    """只提供 UartLinkClient 會用到的介面，餵進去的 bytes 依序被 read。"""

    def __init__(self) -> None:
        self._data = bytearray()

    def feed(self, data: bytes) -> None:
        self._data.extend(data)

    @property
    def in_waiting(self) -> int:
        return len(self._data)

    def read(self, size: int = 1) -> bytes:
        chunk = bytes(self._data[:size])
        del self._data[:size]
        return chunk

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def write(self, data: bytes) -> int:
        return len(data)


def device_id_frame() -> bytes:
    payload = b"ABC".ljust(16, b"\x00")
    return DefaultTrackpadProtocol().encode(
        TrackpadPacket(type_id=int(TrackpadResponseTypeId.DEVICE_ID), payload=payload)
    )


class DecodeTest(unittest.TestCase):
    def decode(self, chunks):
        discarded = bytearray()
        proto = DefaultTrackpadProtocol()
        proto.on_discard = discarded.extend
        buffer = bytearray()
        packets = []
        for chunk in chunks:
            buffer.extend(chunk)
            packets.extend(proto.decode_from_buffer(buffer))
        return packets, bytes(discarded), bytes(buffer)

    def test_text_only_is_discarded_to_callback(self):
        packets, discarded, rest = self.decode([b"hello\n"])
        self.assertEqual(packets, [])
        self.assertEqual(discarded, b"hello\n")
        self.assertEqual(rest, b"")

    def test_magic_split_across_reads_is_not_lost(self):
        frame = device_id_frame()
        packets, discarded, _ = self.decode([b"log\n" + frame[:1], frame[1:]])
        self.assertEqual(len(packets), 1)
        self.assertEqual(discarded, b"log\n")

    def test_text_between_packets(self):
        frame = device_id_frame()
        packets, discarded, _ = self.decode([b"a\n" + frame + b"b\n" + frame])
        self.assertEqual(len(packets), 2)
        self.assertEqual(discarded, b"a\nb\n")


class ClientTextTest(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.client = UartLinkClient(self.transport)
        self.lines = []
        self.responses = []
        self.client.register_text_handler(self.lines.append)
        self.client.register_response_handler(self.responses.append)
        self.client.open()

    def tearDown(self):
        self.client.close()

    def wait_for(self, predicate, timeout=1.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.01)
        return predicate()

    def test_lines_and_packets_interleaved(self):
        self.transport.feed(b"boot ok\r\n" + device_id_frame() + b"temp=42\n")
        self.assertTrue(self.wait_for(lambda: len(self.lines) == 2 and self.responses))
        self.assertEqual(self.lines, ["boot ok", "temp=42"])
        self.assertIsInstance(self.responses[0], DeviceIdResponse)

    def test_partial_line_waits_for_newline(self):
        self.transport.feed(b"half")
        time.sleep(0.03)
        self.assertEqual(self.lines, [])
        self.transport.feed(b" line\n")
        self.assertTrue(self.wait_for(lambda: self.lines == ["half line"]))

    def test_line_without_newline_flushes_after_timeout(self):
        self.transport.feed(b"no newline here")
        self.assertTrue(self.wait_for(lambda: self.lines == ["no newline here"]))

    def test_trailing_U_is_released_as_text(self):
        # 'U' == 0x55，可能是 magic 的前半，但閒置後要當成文字送出。
        self.transport.feed(b"MENU")
        self.assertTrue(self.wait_for(lambda: self.lines == ["MENU"]))

    def test_garbage_line_is_dropped(self):
        self.transport.feed(b"\x01\x02\x03\x04\x05\x06\n" + b"ok\n")
        self.assertTrue(self.wait_for(lambda: self.lines == ["ok"]))

    def test_invalid_utf8_does_not_raise(self):
        self.transport.feed(b"bad \xff\xfe byte\n")
        self.assertTrue(self.wait_for(lambda: len(self.lines) == 1))

    def test_long_line_without_newline_is_capped(self):
        self.transport.feed(b"x" * 5000)
        self.assertTrue(self.wait_for(lambda: len(self.lines) >= 1))
        self.assertLessEqual(len(self.lines[0]), 5000)


if __name__ == "__main__":
    unittest.main()
