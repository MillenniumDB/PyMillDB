import socket
from functools import wraps
from typing import Callable

from . import protocol
from .utils import decorators


class MDBClient:
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.address = (host, port)
        self._sock = None
        self._closed = True
        self._connect()

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._sock.close()
            self._sock = None
            self._closed = True

    def __enter__(self) -> "MDBClient":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def _connect(self) -> None:
        try:
            self._sock = socket.create_connection(self.address)
            self._closed = False
        except ConnectionRefusedError as e:
            raise ConnectionError(
                f"Couldn't connect to MillenniumDB server at {self.address}"
            ) from e

    @decorators.check_closed
    def _send(self, data: bytes) -> None:
        self._sock.sendall(data)

    @decorators.check_closed
    def _recv(self) -> bytes:
        # Each message contains:
        # - 1 bit                : Last message flag
        # - 7 bits               : Status code
        # - 2 bytes              : Data length
        # - Message length bytes : Data
        data = b""
        while True:
            msg = self._sock.recv(protocol.BUFFER_SIZE)
            msg_length = int.from_bytes(msg[1:3], "little")
            data += msg[3 : 3 + msg_length]
            if protocol.last_message(msg[0]):
                break

        # Check if the server threw an exception
        if protocol.decode_status(msg[0]) != protocol.StatusCode.SUCCESS:
            raise Exception(data.decode("utf-8"))
        return data
