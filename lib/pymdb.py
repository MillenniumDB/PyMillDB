# This is a design for the MillenniumDB Python API
# Sources:
#   neo4j: https://neo4j.com/docs/api/python-driver/current/api.html
#   MySQL: https://pymysql.readthedocs.io/en/latest/modules/index.html
import socket


class Connection:
    def __init__(self, host: str = "localhost", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self._sock = None
        self.connect()

    def connect(self) -> None:
        try:
            self._sock = socket.create_connection((self.host, self.port))
        except Exception as _:
            raise ConnectionError(f"Failed to connect to MillenniumDB server at {self.host}:{self.port}")

    def close(self) -> None:
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()
        self._sock = None

    def cursor(self) -> "Cursor":
        return Cursor(self)

class Cursor:
    def __init__(self, connection: "Connection") -> None:
        self.connection = connection

    def execute(self, query: str) -> None:
        self.connection.query(query)

    def close(self):
        # TODO: Exhaust data
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
