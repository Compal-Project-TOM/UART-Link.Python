from __future__ import annotations

import time
from threading import Event, Lock, Thread
from typing import Callable, Optional

from .response import (
    TrackpadResponse,
    default_trackpad_response_decoder,
)
from .models import TrackpadPacket
from .protocol import DefaultTrackpadProtocol, TrackpadProtocol
from .request import TrackpadRequest, validate_trackpad_request
from .transport import SerialTransport

ResponseHandler = Callable[[TrackpadResponse], None]


def _decode_response(packet: TrackpadPacket) -> TrackpadResponse:
    return default_trackpad_response_decoder(packet)


class UartLinkClient:
    def __init__(
            self,
            transport: SerialTransport,
            protocol: Optional[TrackpadProtocol] = None,
    ) -> None:
        self._transport = transport
        self._protocol = protocol or DefaultTrackpadProtocol()
        self._rx_buffer = bytearray()
        self._response_handlers: list[ResponseHandler] = []
        self._handlers_lock = Lock()
        self._stop_event = Event()
        self._rx_thread: Optional[Thread] = None
        self._worker_exception: Optional[BaseException] = None

    def open(self) -> None:
        self._raise_if_worker_failed()
        self._transport.open()
        self._start_receiver_thread()

    def close(self) -> None:
        self._stop_receiver_thread()
        self._transport.close()

    def send(self, type_id: int, payload: bytes = b"") -> int:
        self._raise_if_worker_failed()
        payload_bytes = bytes(payload)
        validate_trackpad_request(type_id, payload_bytes)
        packet = TrackpadPacket(type_id=type_id, payload=payload_bytes)
        frame = self._protocol.encode(packet)
        return self._transport.write(frame)

    def send_request(self, request: TrackpadRequest) -> int:
        self._raise_if_worker_failed()
        return self.send(request.type_id, request.payload)

    def register_response_handler(self, callback: ResponseHandler) -> None:
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._response_handlers.append(callback)

    def unregister_response_handler(self, callback: ResponseHandler) -> None:
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._response_handlers = [h for h in self._response_handlers if h != callback]

    def _start_receiver_thread(self) -> None:
        if self._rx_thread is not None and self._rx_thread.is_alive():
            return
        self._stop_event.clear()
        thread = Thread(target=self._receiver_loop, name="uart-link-rx", daemon=True)
        self._rx_thread = thread
        thread.start()

    def _stop_receiver_thread(self) -> None:
        self._stop_event.set()
        if self._rx_thread is not None:
            self._rx_thread.join(timeout=1.0)
        self._rx_thread = None

    def _receiver_loop(self) -> None:
        try:
            while not self._stop_event.is_set():
                waiting = self._transport.in_waiting
                if waiting:
                    self._rx_buffer.extend(self._transport.read(waiting))
                    packets = list(self._protocol.decode_from_buffer(self._rx_buffer))
                    if packets:
                        self._publish_packets(packets)
                else:
                    time.sleep(0.005)
        except Exception as exc:
            self._worker_exception = exc
            self._stop_event.set()

    def _publish_packets(self, packets: list[TrackpadPacket]) -> None:
        with self._handlers_lock:
            response_handlers_snapshot = list(self._response_handlers)
        for packet in packets:
            response = _decode_response(packet)
            for handler in response_handlers_snapshot:
                handler(response)

    def _raise_if_worker_failed(self) -> None:
        if self._worker_exception is not None:
            raise RuntimeError("UART receiver thread failed") from self._worker_exception
