from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .mdb_client import MDBClient

from .protocol import RequestType, StatusCode
from .utils import decorators, packer


class NodeIterator:
    def __init__(self, client: "MDBClient", batch_size: int) -> None:
        self.client = client
        self.batch_size = batch_size

        self._node_iterator_id = None
        self._size = None
        self._closed = True
        self._new()

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._close()

    def __len__(self) -> int:
        return self.size()

    @decorators.check_closed
    def size(self) -> int:
        return self._size

    @decorators.check_closed
    def __iter__(self) -> "NodeIterator":
        self._begin()
        return self

    @decorators.check_closed
    def __next__(self) -> List[int]:
        return self._next()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.NODE_ITERATOR_NEW)
        msg += packer.pack_uint64(self.batch_size)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._node_iterator_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False

    def _begin(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.NODE_ITERATOR_BEGIN)
        msg += packer.pack_uint64(self._node_iterator_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    def _next(self) -> List[int]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.NODE_ITERATOR_NEXT)
        msg += packer.pack_uint64(self._node_iterator_id)
        self.client._send(msg)

        # Handle response
        data, code = self.client._recv()

        if code == StatusCode.END_OF_ITERATION:
            raise StopIteration

        num_nodes = packer.unpack_uint64(data[0:8])
        lo, hi = 8, 8 + 8 * num_nodes
        return packer.unpack_uint64_vector(data[lo:hi])

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.NODE_ITERATOR_CLOSE)
        msg += packer.pack_uint64(self._node_iterator_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self._batch_loader_id = None
        self._size = None
        self._closed = True

    def __repr__(self) -> str:
        return f"NodeIterator(batch_size={self.batch_size})"
