from typing import List

from .protocol import RequestType
from .utils import decorators, packer


class BatchLoader:
    def __init__(
        self,
        client: "MDBClient",
        feature_store_name: str,
        num_seeds: int,
        batch_size: int,
        neighbor_sizes: List[int],
    ):
        self.client = client
        self.feature_store_name = feature_store_name
        self.num_seeds = num_seeds
        self.batch_size = batch_size
        self.neighbor_sizes = neighbor_sizes

        self._batch_loader_id = None
        self._closed = True
        self._new()

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._close()

    def size() -> int:
        raise NotImplementedError("BatchLoader.size() is not implemented")

    @decorators.check_closed
    def __iter__(self):
        self._begin()
        return self

    @decorators.check_closed
    def __next__(self):
        return self._next()

    def __repr__(self) -> str:
        return (
            "BatchLoader("
            + f"feature_store_name={self.feature_store_name}, "
            + f"num_seeds={self.num_seeds}, "
            + f"batch_size={self.batch_size}, "
            + f"neighbor_sizes={self.neighbor_sizes})"
        )

    def __len__(self) -> int:
        return self.size()

    def _new(self) -> None:
        # Send BATCH_LOADER_NEW request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_NEW)
        msg += packer.pack_uint64(self.num_seeds)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(len(self.neighbor_sizes))
        msg += packer.pack_uint64(len(self.feature_store_name))
        msg += packer.pack_uint64_vector(self.neighbor_sizes)
        msg += packer.pack_string(self.feature_store_name)
        self.client._send(msg)

        # Handle response
        data = self.client._recv()
        self._batch_loader_id = packer.unpack_uint64(data[0:8])
        self._closed = False

    def _begin(self) -> None:
        # Send BATCH_LOADER_BEGIN request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_BEGIN)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    def _next(self) -> "Graph":
        # Send BATCH_LOADER_NEXT request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_NEXT)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        data = self.client._recv()
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

        raise NotImplementedError("BatchLoader.next() not implemented yet")

    def _close(self) -> None:
        # Send BATCH_LOADER_CLOSE request
        msg = b""
        msg += packer.pack_byte(RequestType.BATCH_LOADER_CLOSE)
        msg += packer.pack_uint64(self._batch_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self._batch_loader_id = None
        self._closed = True
