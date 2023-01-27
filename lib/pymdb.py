# This is a design for the MillenniumDB Python API

import socket
import tempfile
import pandas as pd

BYTES_FOR_QUERY_LENGTH = 4
BUFFER_SIZE = 4096
END_MASK = 0x80
STATUS_MASK = 0x7F


class Client:
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.address = (host, port)
        self.is_valid = False
        self._check_connection()

    def _check_connection(self) -> None:
        try:
            with socket.create_connection(self.address) as _:
                self.is_valid = True
        except Exception as _:
            raise ConnectionError(
                f"Couldn't connect Client to MillenniumDB at {self.address}"
            )

    def cursor(self) -> "Cursor":
        return Cursor(self)

    def close(self) -> None:
        self.address = None
        self.is_valid = False

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *_) -> None:
        self.close()


class Cursor:
    def __init__(self, client: "Client") -> None:
        self.client = client
        self._binding = list()
        self._rows = list()
        self._rownumber = 0
        self._sock = None

    def _clear(self) -> None:
        self._binding = list()
        self._rows = list()
        self._rownumber = 0

    def _connect(self) -> None:
        # Check if client is valid
        if not self.client.is_valid:
            raise ConnectionError("Client is not connected to MillenniumDB")
        try:
            self._sock = socket.create_connection(self.client.address)
        except Exception as _:
            raise ConnectionError(
                f"Couldn't connect Cursor to MillenniumDB at {self.client.address}"
            )

    def _send_query(self, query: str) -> None:
        query_bytes = query.encode("utf-8")
        size_bytes = len(query_bytes).to_bytes(
            BYTES_FOR_QUERY_LENGTH, byteorder="little"
        )
        self._sock.send(size_bytes + query_bytes)

    def _parse_file(self, file) -> None:
        file.seek(0)
        # Header
        self._binding = file.readline().decode("utf-8").strip().split(",")
        # Skip separator
        file.readline()
        # Body
        for line in file.readlines():
            line_decoded = line.decode("utf-8").strip()
            if line_decoded[0] != "-":
                self._rows.append(line_decoded.split(","))
            else:
                # Skip separator
                break

    def _recv_result(self) -> None:
        with tempfile.TemporaryFile() as tmp_file:
            result_buffer = bytearray(BUFFER_SIZE)
            while True:
                result_buffer = self._sock.recv(BUFFER_SIZE)
                reply_length = int.from_bytes(result_buffer[1:3], byteorder="little")
                # First 3 bytes are used for the status and length of the message
                tmp_file.write(result_buffer[3 : reply_length - 3])
                if (result_buffer[0] & END_MASK) != 0:
                    break
            status = result_buffer[0] & STATUS_MASK
            if status != 0:
                raise Exception(f"Query failed with status code {status}")
            self._parse_file(tmp_file)

    def execute(self, query: str) -> None:
        # Clear previous results
        self._clear()
        # Establish connection
        self._connect()
        # Send query
        self._send_query(query)
        # Receive results
        self._recv_result()
        # Close connection
        self.close()

    def fetchone(self) -> pd.DataFrame or None:
        if self._rownumber < len(self._rows):
            self._rownumber += 1
            return pd.DataFrame(
                columns=self._binding, data=[self._rows[self._rownumber - 1]]
            )
        return None

    def fetchall(self) -> pd.DataFrame or None:
        if self._rownumber < len(self._rows):
            self._rownumber = len(self._rows)
            return pd.DataFrame(columns=self._binding, data=self._rows)
        return None

    def fetchmany(self, size: int) -> pd.DataFrame or None:
        if self._rownumber < len(self._rows) and size > 0:
            self._rownumber += size
            return pd.DataFrame(
                columns=self._binding,
                data=self._rows[self._rownumber - size : self._rownumber],
            )
        return None

    def close(self):
        if self._sock is not None:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = None

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, *_) -> None:
        self.close()
