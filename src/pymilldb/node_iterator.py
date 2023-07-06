from typing import TYPE_CHECKING, List

from . import packer
from .protocol import RequestType, StatusCode

if TYPE_CHECKING:
    from .mdb_client import MDBClient

## Interface for iterating over nodes in MillenniumDB.
class NodeIterator:
    ## Constructor.
    def __init__(self, client: "MDBClient", batch_size: int) -> None:
        if batch_size <= 0:
            raise ValueError(f"batch_size must be positive integer, got {batch_size}")

        ## Client instance.
        self.client = client
        ## Maximum batch size.
        self.batch_size = batch_size

        self._node_iterator_id = None
        self._create()

    def _create(self) -> None:
        msg = b""
        msg += packer.pack_uint64(self.batch_size)
        self.client._send(RequestType.NODE_ITERATOR_CREATE, msg)

        data, _ = self.client._recv()
        self._node_iterator_id = packer.unpack_uint64(data, 0, 8)

    def __iter__(self) -> "NodeIterator":
        msg = b""
        msg += packer.pack_uint64(self._node_iterator_id)
        self.client._send(RequestType.NODE_ITERATOR_BEGIN, msg)

        self.client._recv()
        return self

    def __next__(self) -> List[int]:
        msg = b""
        msg += packer.pack_uint64(self._node_iterator_id)
        self.client._send(RequestType.NODE_ITERATOR_NEXT, msg)

        data, status = self.client._recv()

        if status == StatusCode.END_OF_ITERATION:
            raise StopIteration

        lo, hi = 0, 8
        num_node_ids = packer.unpack_uint64(data, lo, hi)
        lo, hi = hi, hi + 8 * num_node_ids
        return packer.unpack_uint64_vector(data, lo, hi)
