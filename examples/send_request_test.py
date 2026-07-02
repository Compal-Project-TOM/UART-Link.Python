import argparse
import time

from uart_link import (
    UartConfig,
    UartLinkClient,
    SerialTransport,
    DeviceIdResponse,
    EffectiveActiveAreasResponse,
    CalibrationDataResponse,
    SamplingTimeResponse,
    GetDeviceIdRequest, GetFirmwareVersionRequest, GetInformationRequest, SetSamplingTimeRequest,
    FirmwareVersionResponse, AdcGainResponse, SamplingTooLongResponse, CommandNotSupportedResponse,
    DoCalibrationRequest, RunRequest, StopRequest, SensorFrameChunkResponse,
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
        if isinstance(resp, FirmwareVersionResponse):
            print("firmware_version:", resp.firmware_version)
        if isinstance(resp, CalibrationDataResponse):
            print("calibration_data:", resp.sensor_values)
        if isinstance(resp, SamplingTimeResponse):
            print("sampling_time_us:", resp.sampling_time_us)
        if isinstance(resp, SensorFrameChunkResponse):
            print("sensor_data:", resp.sensor_values)
        if isinstance(resp, AdcGainResponse):
            print("adc:", resp.adc, "gain:", resp.gain)
        if isinstance(resp, SamplingTooLongResponse):
            print("Warning: Sampling Too Long")
        if isinstance(resp, CommandNotSupportedResponse):
            print("Error: Command Not Supported")

    client.register_response_handler(on_response)
    client.open()

    try:
        client.send_request(StopRequest())

        client.send_request(GetDeviceIdRequest())
        client.send_request(GetFirmwareVersionRequest())
        client.send_request(GetInformationRequest())
        time.sleep(1)
        client.send_request(DoCalibrationRequest())
        time.sleep(5)
        client.send_request(RunRequest())
        time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        client.send_request(StopRequest())
        client.unregister_response_handler(on_response)
        client.close()


if __name__ == "__main__":
    main()
