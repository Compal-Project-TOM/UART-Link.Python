import argparse
import time

from uart_link import (
    SensorFrameChunkMessage,
    UartConfig,
    UartLinkClient,
    SerialTransport,
    DeviceIdMessage,
    EffectiveActiveAreasMessage,
    CalibrationDataMessage,
    SamplingTimeMessage,
    SamplingTooLongMessage,
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

    def on_message(message) -> None:
        # print(f"{type(message).__name__}: type_id=0x{message.type_id:02X}")
        if isinstance(message, DeviceIdMessage):
            print("device_id:", message.device_id.decode())
        if isinstance(message, EffectiveActiveAreasMessage):
            print("effective_active_areas:", message.active_area_count)
        if isinstance(message, CalibrationDataMessage):
            print("calibration_data:", message.sensor_values)
        if isinstance(message, SensorFrameChunkMessage):
            print("sensor_values:", message.sensor_values)
        if isinstance(message, SamplingTimeMessage):
            print("sampling_time_us:", message.sampling_time_us)
        if isinstance(message, SamplingTooLongMessage):
            print("Warring: Sampling Too Long")

    client.register_message_handler(on_message)
    client.open()
    print(f"Listening on {args.port} @ {args.baudrate}. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        client.unregister_message_handler(on_message)
        client.close()


if __name__ == "__main__":
    main()
