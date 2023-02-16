import socket
from typing import Tuple

from . import protocol


class MDBClient:
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.address = (host, port)
        self._sock = None
        self._closed = True
        self._connect()

    def close(self) -> None:
        self._sock.close()
        self._sock = None
        self.closed = True

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

    def _send(self, data: bytes) -> None:
        if self._closed:  # TODO: DECORATOR?
            raise ConnectionError("Client is not connected to MillenniumDB")
        self._sock.sendall(data)

    def _recv(self) -> bytes:
        # Each response contains:
        # - 1 bit                : Last message flag
        # - 7 bits               : Status code
        # - 2 bytes              : Message length
        # - Message length bytes : Message
        if self._closed:  # TODO: DECORATOR?
            raise ConnectionError("Client is not connected to MillenniumDB")
        data = b""
        while True:
            msg = self._sock.recv(protocol.BUFFER_SIZE)
            msg_length = int.from_bytes(msg[1:3], "little")
            print(msg_length)
            data += msg[3 : 3 + msg_length]
            if protocol.last_message(msg[0]):
                break
        # Check if PyMDB server has thrown an exception
        if protocol.decode_status(msg[0]) != protocol.StatusCode.SUCCESS:
            raise Exception(data.decode("utf-8"))
        return data
