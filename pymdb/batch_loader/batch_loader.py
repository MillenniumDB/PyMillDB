# NOTE: The uint64 vectors are parsed as int64 vectors due the lack of the uint64 dtype
# in the torch.Tensor class.

import abc

import torch

from ..mdb_client.protocol import RequestType, StatusCode
from ..utils import decorators, packer
from ..utils.graph import Graph


class BatchLoader(abc.ABC):
    @abc.abstractclassmethod
    def __init__(self, *args) -> None:
        pass

    @abc.abstractmethod
    def _new(self, *args) -> None:
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass

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
    def __iter__(self) -> "BatchLoader":
        self._begin()
        return self

    @decorators.check_closed
    def __next__(self) -> Graph:
        return self._next()

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
        num_seeds = packer.unpack_uint64(data[16:24])
        feature_size = packer.unpack_uint64(data[24:32])

        lo, hi = 32, 32 + 4 * num_nodes * feature_size
        node_features = torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
        ).reshape(num_nodes, feature_size)

        lo, hi = hi, hi + 8 * num_nodes
        node_labels = torch.tensor(
            data=packer.unpack_uint64_vector(data[lo:hi]), dtype=torch.int64
        )

        lo, hi = hi, hi + 8 * 2 * num_edges
        edge_index = torch.tensor(
            data=packer.unpack_uint64_vector(data[lo:hi]), dtype=torch.int64
        ).reshape(2, num_edges)

        lo, hi = hi, hi + 8 * num_nodes
        node_ids = packer.unpack_uint64_vector(data[lo:hi])

        return Graph(
            node_features,
            node_labels,
            edge_index,
            node_ids,
            num_seeds,
            feature_size,
        )

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
