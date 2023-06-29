import socket
from typing import Tuple

from . import decorators, packer, protocol


## Interface for stablishing a connection with the server for
# sending and receiving data.
#
# Almost every class and function in this library needs a `MDBClient` instance
# as an argument to communicate with the server.
class MDBClient:
    ## Constructor.
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        ## Address of the server.
        self.address = (host, port)

        self._sock = None
        self._closed = True
        self._connect()

    ## Returns `True` if the connection with the server is closed.
    def is_closed(self) -> bool:
        return self._closed

    ## Closes the connection with the server.
    def close(self) -> None:
        if not self._closed:
            self._sock.close()
            self._sock = None
            self._closed = True

    ## Enter context manager.
    def __enter__(self) -> "MDBClient":
        return self

    ## Exit context manager.
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
    def _send(self, request_type: protocol.RequestType, data: bytes) -> None:
        header = packer.pack_byte(request_type) + packer.pack_uint64(len(data))
        self._sock.sendall(header + data)

    @decorators.check_closed
    def _recv(self) -> Tuple[bytes, protocol.StatusCode]:
        # Helper function to receive exactly `length` bytes
        def recvall(length: int) -> bytes:
            data = b""
            while len(data) < length:
                msg = self._sock.recv(length - len(data))
                if len(msg) == 0:
                    raise ConnectionError("Server closed the connection")
                data += msg
            return data

        # Each message contains:
        # - 1 bit                      : Last message flag
        # - 7 bits                     : Status code
        # - 2 bytes                    : message.size()
        # - (message.size() - 3) bytes : Data
        data = b""
        while True:
            msg = recvall(protocol.BUFFER_SIZE)
            msg_size = int.from_bytes(msg[1:3], "little")
            data += msg[3:msg_size]
            if protocol.last_message(msg[0]):
                break

        # Check if the server threw an exception
        if protocol.error_status(msg[0]):
            raise Exception(data.decode("utf-8"))
        return data, protocol.decode_status(msg[0])
