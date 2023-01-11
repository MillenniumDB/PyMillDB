import socket

class Client:
    def __init__(self, host: str, port: int):
        self.addr = (host, port)
        self.sock = socket.create_connection(self.addr)

    def query(self, query: str):
        query_b = query.encode("utf-8")
        size_b  = len(query_b).to_bytes(4, byteorder="little")
        self.sock.send(size_b + query_b)

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
