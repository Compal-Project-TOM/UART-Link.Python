from __future__ import annotations

import time
from threading import Event, Lock, Thread
from typing import Callable, Optional

from .messages import (
    TrackpadMessage,
    default_trackpad_message_decoder,
)
from .models import TrackpadPacket
from .protocol import DefaultTrackpadProtocol, TrackpadProtocol
from .transport import SerialTransport

MessageHandler = Callable[[TrackpadMessage], None]


def _decode_message(packet: TrackpadPacket) -> TrackpadMessage:
    return default_trackpad_message_decoder(packet)


class UartLinkClient:
    def __init__(
            self,
            transport: SerialTransport,
            protocol: Optional[TrackpadProtocol] = None,
    ) -> None:
        self._transport = transport
        self._protocol = protocol or DefaultTrackpadProtocol()
        self._rx_buffer = bytearray()
        self._message_handlers: list[MessageHandler] = []
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
        packet = TrackpadPacket(type_id=type_id, payload=payload)
        frame = self._protocol.encode(packet)
        return self._transport.write(frame)

    def register_message_handler(self, callback: MessageHandler) -> None:
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._message_handlers.append(callback)

    def unregister_message_handler(self, callback: MessageHandler) -> None:
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._message_handlers = [h for h in self._message_handlers if h != callback]

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
            message_handlers_snapshot = list(self._message_handlers)
        for packet in packets:
            message = _decode_message(packet)
            for handler in message_handlers_snapshot:
                handler(message)

    def _raise_if_worker_failed(self) -> None:
        if self._worker_exception is not None:
            raise RuntimeError("UART receiver thread failed") from self._worker_exception
