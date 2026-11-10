import unittest

from uart_link import AdcGain, AdcGainResponse, SetAdcGainRequest, TrackpadPacket
from uart_link.response import default_trackpad_response_decoder
from uart_link.type_ids import TrackpadResponseTypeId


class SetAdcGainRequestTest(unittest.TestCase):
    def test_codes_match_firmware(self) -> None:
        # FW adc_gain_num: GAIN_1 = 0b000 ... GAIN_128 = 0b111
        self.assertEqual([g.name for g in AdcGain], [f"GAIN_{2 ** i}" for i in range(8)])
        self.assertEqual([int(g) for g in AdcGain], list(range(8)))

    def test_valid_gains(self) -> None:
        for gain in list(AdcGain) + list(range(8)):
            with self.subTest(gain=gain):
                req = SetAdcGainRequest(1, gain)
                self.assertEqual(req.payload, bytes([1, 0, int(gain)]))

    def test_multiplier(self) -> None:
        for gain in AdcGain:
            with self.subTest(gain=gain):
                self.assertEqual(gain.multiplier, int(gain.name.removeprefix("GAIN_")))
                resp = default_trackpad_response_decoder(
                    TrackpadPacket(
                        type_id=int(TrackpadResponseTypeId.ADC_GAIN),
                        payload=bytes([1, 0, int(gain)]),
                    )
                )
                self.assertIsInstance(resp, AdcGainResponse)
                self.assertEqual(resp.gain, int(gain))
                self.assertEqual(resp.gain_multiplier, gain.multiplier)

    def test_invalid_gains(self) -> None:
        for gain in (-1, 8, 16, 128, True, 3.0, "3", None):
            with self.subTest(gain=gain):
                with self.assertRaises(ValueError):
                    SetAdcGainRequest(0, gain)


if __name__ == "__main__":
    unittest.main()
