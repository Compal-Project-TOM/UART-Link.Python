import argparse
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from uart_link import (
    SensorFrameChunkResponse,
    UartConfig,
    UartLinkClient,
    SerialTransport,
    CalibrationDataResponse,
    SamplingTimeResponse,
    SamplingTooLongResponse, StopRequest, DoCalibrationRequest, RunRequest, SetSamplingTimeRequest, SetAdcGainRequest,
)

sensor_count = 22*12
columns = ['timestamp'] + [f'sensor_{i}' for i in range(sensor_count)]
data_buffer = []
adc_gain = 1

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read UART packets from trackpad device with uart_link."
    )
    parser.add_argument("--port", required=True, help="Serial port, e.g. COM3")
    parser.add_argument("--baudrate", type=int, default=3000000, help="UART baudrate")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    return parser


def draw_figures(df: pd.DataFrame, fps, vpp) -> None:
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    if not sensor_cols:
        raise ValueError("No sensor columns found in DataFrame.")

    time_axis = df['datatime'] if 'datatime' in df.columns else pd.to_datetime(df['timestamp'], unit='s')

    plt.figure(figsize=(16, 8))
    for sensor_col in sensor_cols:
        plt.plot(time_axis, df[sensor_col], linewidth=1.0, alpha=0.8, label=sensor_col)

    max_sensor = vpp.idxmax()
    min_sensor = vpp.idxmin()
    plt.title(f"[Gain x{adc_gain}]    "
              f"FPS: {fps.mean()} (mean) / {fps.max()} (max) / {fps.min()} (min)    "
              f"Vp-p: {vpp[max_sensor]} mv (max, at {max_sensor}) / {vpp[min_sensor]} mv (min, at {min_sensor})")
    plt.xlabel("Time")
    plt.ylabel("Value (mV)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def sensor_data_analysis(df: pd.DataFrame):
    df['datatime'] = pd.to_datetime(df['timestamp'], unit='s')

    print("\n----- Analysis Results -----")

    # Calculate fps
    fps = df.set_index('datatime').resample('1s').size().iloc[1:-1]
    print("\n*** FPS ***")
    print("Average:", fps.mean())
    print("Max:", fps.max())
    print("Min:", fps.min())

    # Calculate Vp-p
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')]
    vpp = df[sensor_cols].apply(np.ptp)
    print("\n*** Vp-p ***")
    max_sensor = vpp.idxmax()
    min_sensor = vpp.idxmin()
    print(f"Max: {vpp[max_sensor]} mv (at {max_sensor})")
    print(f"Min: {vpp[min_sensor]} mv (at {min_sensor})")

    draw_figures(df, fps, vpp)


def main() -> None:
    args = build_parser().parse_args()

    config = UartConfig(port=args.port, baudrate=args.baudrate)
    transport = SerialTransport(config)
    client = UartLinkClient(transport)

    def on_response(resp) -> None:
        if isinstance(resp, CalibrationDataResponse):
            print("calibration_data:", resp.sensor_values)
        if isinstance(resp, SensorFrameChunkResponse):
            print(resp.sensor_values)
            current_time = time.time()
            row_data = [current_time] + list(resp.sensor_values)
            data_buffer.append(row_data)
        if isinstance(resp, SamplingTimeResponse):
            print("sampling_time_us:", resp.sampling_time_us)
        if isinstance(resp, SamplingTooLongResponse):
            print("Warning: Sampling Too Long")

    client.register_response_handler(on_response)
    client.open()
    print(f"Listening on {args.port} @ {args.baudrate}. Press Ctrl+C to stop.")

    try:
        client.send_request(StopRequest())

        # client.send_request(SetSamplingTimeRequest(10500))

        client.send_request(SetAdcGainRequest(0, adc_gain))
        client.send_request(SetAdcGainRequest(1, adc_gain))

        client.send_request(DoCalibrationRequest())
        time.sleep(5)

        client.send_request(RunRequest())
        time.sleep(args.duration)
        client.send_request(StopRequest())
        time.sleep(0.5)

        df = pd.DataFrame(data_buffer, columns=columns)
        sensor_data_analysis(df)

    except KeyboardInterrupt:
        pass
    finally:
        client.send_request(StopRequest())
        client.unregister_response_handler(on_response)
        client.close()


if __name__ == "__main__":
    main()
