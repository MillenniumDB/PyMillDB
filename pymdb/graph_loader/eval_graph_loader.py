from typing import TYPE_CHECKING, List

from ..protocol import RequestType
from ..utils import packer
from .graph_loader import GraphLoader

if TYPE_CHECKING:
    from ..mdb_client import MDBClient


class EvalGraphLoader(GraphLoader):
    def __init__(
        self,
        client: "MDBClient",
        tensor_store_name: str,
        batch_size: int,
        num_neighbors: List[int],
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        if len(num_neighbors) == 0:
            raise ValueError("num_neighbors must be non-empty")

        self.client = client
        self.tensor_store_name = tensor_store_name
        self.batch_size = batch_size
        # Convert negative values to max uint64 value
        self.num_neighbors = list(
            map(lambda x: 2**64 - 1 if x < 0 else x, num_neighbors)
        )

        self._graph_loader_id = None
        self._size = None
        self._closed = True
        self._new()
        self._begin()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.EVAL_GRAPH_LOADER_NEW)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(len(self.num_neighbors))
        msg += packer.pack_uint64(len(self.tensor_store_name))
        msg += packer.pack_uint64_vector(self.num_neighbors)
        msg += packer.pack_string(self.tensor_store_name)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._graph_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f'tensor_store_name="{self.tensor_store_name}", '
            f"batch_size={self.batch_size}, "
            f"num_neighbors={self.num_neighbors})"
        )
