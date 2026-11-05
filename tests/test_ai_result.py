import struct
import unittest

from uart_link import (
    AiInferenceTimeResponse,
    AiTouchResultResponse,
    DefaultTrackpadProtocol,
    GetAiInferenceTimeRequest,
    ReportMode,
    ReportModeResponse,
    SetReportModeRequest,
    TrackpadPacket,
)
from uart_link.response import default_trackpad_response_decoder
from uart_link.type_ids import TrackpadRequestTypeId, TrackpadResponseTypeId


def decode(type_id: int, payload: bytes):
    return default_trackpad_response_decoder(TrackpadPacket(type_id=int(type_id), payload=payload))


class RequestTest(unittest.TestCase):
    def test_set_report_mode_payload(self):
        req = SetReportModeRequest(ReportMode.SENSOR_FRAME_CHUNK | ReportMode.AI_TOUCH_RESULT)
        self.assertEqual(req.type_id, 0x12)
        self.assertEqual(req.payload, b"\x03")

    def test_set_report_mode_encodes_to_frame(self):
        frame = DefaultTrackpadProtocol().encode(SetReportModeRequest(ReportMode.AI_TOUCH_RESULT).to_packet())
        self.assertEqual(frame, b"\x55\xAA\x12\x00\x01\x02")

    def test_set_report_mode_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            SetReportModeRequest(0x100)

    def test_get_ai_inference_time(self):
        req = GetAiInferenceTimeRequest()
        self.assertEqual(req.type_id, int(TrackpadRequestTypeId.GET_AI_INFERENCE_TIME))
        self.assertEqual(req.payload, b"")


class ReportModeResponseTest(unittest.TestCase):
    def test_decode(self):
        resp = decode(TrackpadResponseTypeId.REPORT_MODE, b"\x02")
        self.assertIsInstance(resp, ReportModeResponse)
        self.assertEqual(resp.mode, ReportMode.AI_TOUCH_RESULT)
        self.assertNotIn(ReportMode.SENSOR_FRAME_CHUNK, resp.mode)

    def test_wrong_length(self):
        with self.assertRaises(ValueError):
            decode(TrackpadResponseTypeId.REPORT_MODE, b"")


class AiTouchResultResponseTest(unittest.TestCase):
    def test_no_fingers(self):
        resp = decode(TrackpadResponseTypeId.AI_TOUCH_RESULT, struct.pack(">IBB", 42, 0x01, 0))
        self.assertIsInstance(resp, AiTouchResultResponse)
        self.assertEqual(resp.frame_index, 42)
        self.assertTrue(resp.baseline_ready)
        self.assertEqual(resp.fingers, ())

    def test_two_fingers(self):
        payload = (
            struct.pack(">IBB", 0x01020304, 0x00, 2)
            + struct.pack(">BBHHB", 0, 0x01, 1234, 5900, 255)  # active
            + struct.pack(">BBHHB", 3, 0x02, 10700, 0, 128)  # just lifted
        )
        resp = decode(TrackpadResponseTypeId.AI_TOUCH_RESULT, payload)
        self.assertEqual(resp.frame_index, 0x01020304)
        self.assertFalse(resp.baseline_ready)
        self.assertEqual(len(resp.fingers), 2)

        first, second = resp.fingers
        self.assertEqual(first.contact_id, 0)
        self.assertTrue(first.active)
        self.assertFalse(first.just_lifted)
        self.assertEqual(first.x, 1234)
        self.assertAlmostEqual(first.x_mm, 12.34)
        self.assertAlmostEqual(first.y_mm, 59.0)
        self.assertAlmostEqual(first.confidence_ratio, 1.0)

        self.assertEqual(second.contact_id, 3)
        self.assertFalse(second.active)
        self.assertTrue(second.just_lifted)
        self.assertAlmostEqual(second.x_mm, 107.0)
        self.assertEqual(second.confidence, 128)

    def test_length_must_match_finger_count(self):
        payload = struct.pack(">IBB", 1, 0, 2) + struct.pack(">BBHHB", 0, 1, 0, 0, 0)
        with self.assertRaises(ValueError):
            decode(TrackpadResponseTypeId.AI_TOUCH_RESULT, payload)

    def test_too_short(self):
        with self.assertRaises(ValueError):
            decode(TrackpadResponseTypeId.AI_TOUCH_RESULT, b"\x00\x00\x00")

    def test_round_trip_through_protocol(self):
        payload = struct.pack(">IBB", 7, 1, 1) + struct.pack(">BBHHB", 1, 1, 500, 600, 200)
        frame = DefaultTrackpadProtocol().encode(
            TrackpadPacket(type_id=int(TrackpadResponseTypeId.AI_TOUCH_RESULT), payload=payload)
        )
        packets = list(DefaultTrackpadProtocol().decode_from_buffer(bytearray(frame)))
        resp = default_trackpad_response_decoder(packets[0])
        self.assertEqual(resp.fingers[0].contact_id, 1)
        self.assertAlmostEqual(resp.fingers[0].y_mm, 6.0)


class AiInferenceTimeResponseTest(unittest.TestCase):
    def test_decode(self):
        resp = decode(TrackpadResponseTypeId.AI_INFERENCE_TIME, struct.pack(">5I", 99, 1500, 1000, 300, 200))
        self.assertIsInstance(resp, AiInferenceTimeResponse)
        self.assertEqual(
            (resp.frame_index, resp.total_us, resp.model_us, resp.pre_us, resp.post_us),
            (99, 1500, 1000, 300, 200),
        )

    def test_wrong_length(self):
        with self.assertRaises(ValueError):
            decode(TrackpadResponseTypeId.AI_INFERENCE_TIME, b"\x00" * 16)


if __name__ == "__main__":
    unittest.main()
