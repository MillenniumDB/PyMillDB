import pandas as pd
import socket
import tempfile

BYTES_FOR_QUERY_LENGTH = 4
BUFFER_SIZE = 4096
END_MASK = 0x80
STATUS_MASK = 0x7F

class Result:
    def __init__(self):
        self.tmp_file = tempfile.TemporaryFile()

    def append(self, chunk: bytes):
        self.tmp_file.write(chunk)

    def to_dataframe(self):
        self.tmp_file.seek(0)
        return pd.read_csv(self.tmp_file)

class Client:
    def __init__(self, host: str, port: int):
        self.addr = (host, port)
        self.sock = socket.create_connection(self.addr)

    def query(self, query: str) -> int:
        # Send the query to the server
        query_bytes = query.encode("utf-8")
        size_bytes = len(query_bytes).to_bytes(
            BYTES_FOR_QUERY_LENGTH, byteorder="little"
        )
        self.sock.send(size_bytes + query_bytes)
        # Receive the response from the server
        result_buffer = bytearray(BUFFER_SIZE)
        result = Result()
        while True:
            result_buffer = self.sock.recv(BUFFER_SIZE)
            reply_length = int.from_bytes(result_buffer[1:3], byteorder="little")
            # First 3 bytes are used for the status and tlength of the message
            result.append(result_buffer[3:reply_length - 3])
            if (result_buffer[0] & END_MASK) != 0:
                break
        status = result_buffer[0] & STATUS_MASK
        if status != 0:
            raise Exception(f"Query failed with status code {status}")
        return result

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
