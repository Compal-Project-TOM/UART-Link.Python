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
    DoCalibrationRequest, RunRequest, StopRequest, SensorFrameChunkResponse, SetAdcGainRequest,
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

    # Define a response handler to process incoming responses
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

    # Register response handler
    client.register_response_handler(on_response)

    # Open the UART link
    client.open()

    try:
        # Send a Stop request avoid the device to be in running state before sending other requests
        client.send_request(StopRequest())

        # Get DeviceID, FirmwareVersion and Information
        client.send_request(GetDeviceIdRequest())
        client.send_request(GetFirmwareVersionRequest())
        client.send_request(GetInformationRequest())
        time.sleep(1)

        # Modify Sampling Time
        client.send_request(SetSamplingTimeRequest(11000))

        # Change ADC gain to x8
        client.send_request(SetAdcGainRequest(0, 8))
        client.send_request(SetAdcGainRequest(1, 8))

        # Do calibration before run (optional)
        client.send_request(DoCalibrationRequest())
        time.sleep(5)

        # Start running
        client.send_request(RunRequest())
        time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        # Send Stop request before closing the client
        client.send_request(StopRequest())
        client.unregister_response_handler(on_response)
        client.close()


if __name__ == "__main__":
    main()
