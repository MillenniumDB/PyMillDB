from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .mdb_client import MDBClient

from .protocol import RequestType, StatusCode
from .utils import decorators, packer
from .utils.graph import Graph


class BatchLoader:
    def __init__(
        self,
        client: MDBClient,
        feature_store_name: str,
        num_seeds: int,
        batch_size: int,
        neighbor_sizes: Tuple[int],
        seed: int = 42,
    ) -> None:
        self.client = client
        self.feature_store_name = feature_store_name
        self.num_seeds = num_seeds
        self.batch_size = batch_size
        self.neighbor_sizes = neighbor_sizes
        self.seed = seed

        self._batch_loader_id = None
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
    def __iter__(self):
        self._begin()
        return self

    @decorators.check_closed
    def __next__(self):
        return self._next()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_NEW)
        msg += packer.pack_uint64(self.num_seeds)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(self.seed)
        msg += packer.pack_uint64(len(self.neighbor_sizes))
        msg += packer.pack_uint64(len(self.feature_store_name))
        msg += packer.pack_uint64_vector(self.neighbor_sizes)
        msg += packer.pack_string(self.feature_store_name)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._batch_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False

    def _begin(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_BEGIN)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    def _next(self) -> Graph:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_NEXT)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        data, code = self.client._recv()

        if code == StatusCode.END_OF_ITERATION:
            raise StopIteration

        num_nodes = packer.unpack_uint64(data[0:8])
        num_edges = packer.unpack_uint64(data[8:16])
        feature_size = packer.unpack_uint64(data[16:24])
        lo, hi = 24, 24 + 4 * num_nodes * feature_size
        node_features = packer.unpack_float_vector(
            data[lo:hi], (num_nodes, feature_size)
        )
        lo, hi = hi, hi + 8 * num_nodes
        node_labels = packer.unpack_uint64_vector(data[lo:hi])
        lo, hi = hi, hi + 8 * 2 * num_edges
        edge_index = packer.unpack_uint64_vector(data[lo:hi], (num_edges, 2))
        return Graph(node_features, node_labels, edge_index)

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_CLOSE)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self._batch_loader_id = None
        self._size = None
        self._closed = True

    def __repr__(self) -> str:
        return (
            f'BatchLoader(feature_store_name="{self.feature_store_name}", '
            + f"num_seeds={self.num_seeds}, "
            + f"batch_size={self.batch_size}, "
            + f"neighbor_sizes={self.neighbor_sizes}, "
            + f"seed={self.seed})"
        )
