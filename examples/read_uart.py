import argparse
import time

from uart_link import (
    SensorFrameChunkResponse,
    UartConfig,
    UartLinkClient,
    SerialTransport,
    DeviceIdResponse,
    EffectiveActiveAreasResponse,
    CalibrationDataResponse,
    SamplingTimeResponse,
    SamplingTooLongResponse,
    AdcGainResponse, SetAdcGainRequest, DoCalibrationRequest
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read UART packets from trackpad device with uart_link."
    )
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM3")
    parser.add_argument("--baudrate", type=int, default=3000000, help="UART baudrate")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = UartConfig(port=args.port, baudrate=args.baudrate)
    transport = SerialTransport(config)
    client = UartLinkClient(transport)

    def on_response(resp) -> None:
        # print(f"{type(resp).__name__}: type_id=0x{resp.type_id:02X}")
        if isinstance(resp, DeviceIdResponse):
            print("device_id:", resp.device_id)
        if isinstance(resp, EffectiveActiveAreasResponse):
            print("effective_active_areas:", resp.active_area_count)
        if isinstance(resp, CalibrationDataResponse):
            print("calibration_data:", resp.sensor_values)
        if isinstance(resp, SensorFrameChunkResponse):
            print("sensor_values:", resp.sensor_values)
        if isinstance(resp, SamplingTimeResponse):
            print("sampling_time_us:", resp.sampling_time_us)
        if isinstance(resp, SamplingTooLongResponse):
            print("Warning: Sampling Too Long")
        if isinstance(resp, AdcGainResponse):
            print("adc", resp.adc, "gain:", resp.gain)

    client.register_response_handler(on_response)
    client.open()
    print(f"Listening on {args.port} @ {args.baudrate}. Press Ctrl+C to stop.")

    try:
        adc_gain = 8
        client.send_request(SetAdcGainRequest(0, adc_gain))
        client.send_request(SetAdcGainRequest(1, adc_gain))

        client.send_request(DoCalibrationRequest())
        time.sleep(5)

        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        client.unregister_response_handler(on_response)
        client.close()


if __name__ == "__main__":
    main()
