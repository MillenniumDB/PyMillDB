from typing import TYPE_CHECKING, List

import torch

if TYPE_CHECKING:
    from .mdb_client import MDBClient

from .protocol import RequestType
from .utils import decorators, packer


class FeatureStore:
    def __init__(
        self,
        client: "MDBClient",
        name: str,
        feature_store_id: int,
        feature_size: int,
    ) -> None:
        self.client = client
        self.name = name
        self.feature_size = feature_size

        self._feature_store_id = feature_store_id
        self._closed = False

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._close()

    def __len__(self) -> int:
        return self.size()

    def __enter__(self) -> "FeatureStore":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    @decorators.check_closed
    def size(self) -> int:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_SIZE)
        msg += packer.pack_uint64(self._feature_store_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_uint64(data[0:8])

    @decorators.check_closed
    def contains(self, node_id: int) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_CONTAINS)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_bool(data[0:1])

    @decorators.check_closed
    def insert_tensor(self, node_id: int, tensor: List[float]) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_INSERT_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        msg += packer.pack_uint64(len(tensor))
        msg += packer.pack_float_vector(tensor)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    @decorators.check_closed
    def remove_tensor(self, node_id: int) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_REMOVE_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    @decorators.check_closed
    def get_tensor(self, node_id: int) -> torch.Tensor:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_GET_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.feature_size
        return torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
        )

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_CLOSE)
        msg += packer.pack_uint64(self._feature_store_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self._feature_store_id = None
        self._closed = True

    def __repr__(self) -> str:
        return f'FeatureStore(name="{self.name}", feature_size={self.feature_size})'
