import socket

BYTES_FOR_QUERY_LENGTH = 4
BUFFER_SIZE = 4096
END_MASK = 0x80
STATUS_MASK = 0x7F

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
        while True:
            result_buffer = self.sock.recv(BUFFER_SIZE)
            reply_length = int.from_bytes(result_buffer[1:3], byteorder="little")
            # First 3 bytes are used for the status and tlength of the message
            print(result_buffer[3:reply_length - 3].decode("utf-8"))
            if (result_buffer[0] & END_MASK) != 0:
                break
        return result_buffer[0] & STATUS_MASK

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
