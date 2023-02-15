import socket


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
        if self._closed:
            raise ConnectionError("Client is not connected to MillenniumDB")
        self._sock.sendall(data)

    def _recv(self, nbytes: int) -> bytes:
        if self._closed:
            raise ConnectionError("Client is not connected to MillenniumDB")
        self._sock.recv(nbytes)
