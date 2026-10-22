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
TextHandler = Callable[[str], None]

# 裝置 log 文字：沒收到換行時，閒置超過這段時間就把殘留當成一行送出。
_TEXT_FLUSH_TIMEOUT_S = 0.1
# 文字緩衝上限，避免一直收到沒有換行的雜訊時無限長大。
_TEXT_BUFFER_LIMIT = 4096
# 一行裡不可列印的 byte 比例超過這個值就視為雜訊（例如封包錯位）而丟掉。
_TEXT_MAX_GARBAGE_RATIO = 0.3


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
        self._text_handlers: list[TextHandler] = []
        self._text_buffer = bytearray()
        self._last_rx_time = time.monotonic()
        self._protocol.on_discard = self._on_discarded
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

    def register_text_handler(self, callback: TextHandler) -> None:
        """註冊裝置 log 文字的 callback：封包以外收到的內容會依換行切成一行一行傳入。

        callback 在接收 thread 被呼叫，請保持輕量。
        """
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._text_handlers.append(callback)

    def unregister_text_handler(self, callback: TextHandler) -> None:
        self._raise_if_worker_failed()
        with self._handlers_lock:
            self._text_handlers = [h for h in self._text_handlers if h != callback]

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
                    self._last_rx_time = time.monotonic()
                    self._rx_buffer.extend(self._transport.read(waiting))
                    packets = list(self._protocol.decode_from_buffer(self._rx_buffer))
                    if packets:
                        self._publish_packets(packets)
                else:
                    self._flush_idle_text()
                    time.sleep(0.005)
        except Exception as exc:
            self._worker_exception = exc
            self._stop_event.set()

    def _on_discarded(self, data: bytes) -> None:
        """protocol 丟掉的非封包 byte：累積成文字，依換行切行後送給 text handler。"""
        self._text_buffer.extend(data)
        lines: list[bytes] = []
        while True:
            end = self._text_buffer.find(b"\n")
            if end < 0:
                break
            lines.append(bytes(self._text_buffer[:end]))
            del self._text_buffer[:end + 1]
        if len(self._text_buffer) >= _TEXT_BUFFER_LIMIT:
            lines.append(bytes(self._text_buffer))
            self._text_buffer.clear()
        self._publish_text(lines)

    def _flush_idle_text(self) -> None:
        if time.monotonic() - self._last_rx_time < _TEXT_FLUSH_TIMEOUT_S:
            return
        # 0x55（'U'）可能是 magic 的前半而被 protocol 留在 rx buffer；閒置這麼久還沒等到 0xAA，就當文字。
        magic_head = self._rx_buffer[:1]
        if self._rx_buffer == magic_head and magic_head == b"\x55":
            self._text_buffer.extend(self._rx_buffer)
            self._rx_buffer.clear()
        if self._text_buffer:
            line = bytes(self._text_buffer)
            self._text_buffer.clear()
            self._publish_text([line])

    def _publish_text(self, lines: list[bytes]) -> None:
        decoded = [text for text in (self._decode_text_line(raw) for raw in lines) if text]
        if not decoded:
            return
        with self._handlers_lock:
            handlers = list(self._text_handlers)
        for text in decoded:
            for handler in handlers:
                handler(text)

    @staticmethod
    def _decode_text_line(raw: bytes) -> str:
        raw = raw.rstrip(b"\r")
        if not raw:
            return ""
        # 可列印 ASCII、tab 與高位元組（UTF-8 多位元組字元）都算正常。
        garbage = sum(1 for b in raw if b < 0x20 and b != 0x09 or b == 0x7F)
        if garbage / len(raw) > _TEXT_MAX_GARBAGE_RATIO:
            return ""
        text = raw.decode("utf-8", errors="replace")
        return "".join(ch for ch in text if ch >= " " or ch == "\t").rstrip()

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
