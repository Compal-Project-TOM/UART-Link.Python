import argparse
import time

from uart_link import TrackpadTypeId, UartConfig, UartLinkClient, SerialTransport


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

    def on_packet(packet) -> None:
        print(f"type_id=0x{packet.type_id:02X}, payload={packet.payload.hex()}")
        if packet.type_id == TrackpadTypeId.DEVICE_ID:
            print("Device ID packet received")

    client.register_packet_handler(on_packet)
    client.open()
    print(f"Listening on {args.port} @ {args.baudrate}. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        client.unregister_packet_handler(on_packet)
        client.close()


if __name__ == "__main__":
    main()
