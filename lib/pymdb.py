# This is a design for the MillenniumDB Python API

from typing import Literal
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
        header_str = file.readline().decode("utf-8").strip()
        file.readline()  # Skip first separator
        if header_str == "":
            # Handle empty bindings creating a DataFrame with a single
            # column valued as None and each row has a None value
            self._binding = [None]
            for line in file.readlines():
                line_decoded = line.decode("utf-8").strip()
                if len(line_decoded) and line_decoded[0] == "-":  # Skip last separator
                    break
                self._rows.append(None)
        else:
            self._binding = header_str.split(",")
        # Body
        for line in file.readlines():
            line_decoded = line.decode("utf-8").strip()
            if len(line_decoded) and line_decoded[0] == "-":  # Skip last separator
                break
            self._rows.append(line_decoded.split(","))

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

    def _execute(self, query: str) -> None:
        # Establish connection
        self._connect()
        # Send query
        self._send_query(query)
        # Receive results
        self._recv_result()
        # Close connection
        self.close()

    def execute(self, query: str) -> None:
        # Clear previous results
        self._clear()
        # Execute query
        self._execute(query)

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

    def neighbors(
        self, node: str, edge_type: str = "", direction: Literal["ANY", "OUT", "IN"] = "ANY"
    ) -> pd.DataFrame:
        # Handle empty node
        if node == "":
            raise ValueError("Node can't be empty: " + str(node))
        # Handle variable node
        if node[0] == "?":
            raise ValueError("Node can't be a variable: " + str(node))
        # Handle non-empty edge type
        if edge_type != "":
            edge_type = ":" + str(edge_type)
        # Handle direction
        if direction == "OUT":
            query = f"MATCH ({node})-[{edge_type}]->(?neighbor) RETURN ?neighbor"
            self.execute(query)
        elif direction == "IN":
            query = f"MATCH ({node})<-[{edge_type}]-(?neighbor) RETURN ?neighbor"
            self.execute(query)
        elif direction == "ANY":
            query_out = f"MATCH ({node})-[{edge_type}]->(?neighbor) RETURN ?neighbor"
            self.execute(query_out)
            query_in  = f"MATCH ({node})<-[{edge_type}]-(?neighbor) RETURN ?neighbor"
            self._execute(query_in) # This method won't clear previous results
        else:
            raise ValueError("Invalid direction: " + str(direction))

    def close(self):
        if self._sock is not None:
            self._sock.shutdown(socket.SHUT_RDWR)
            self._sock.close()
            self._sock = None

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(self, *_) -> None:
        self.close()
