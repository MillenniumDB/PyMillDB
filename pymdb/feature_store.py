from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .mdb_client import MDBClient

from .protocol import RequestType
from .utils import decorators, packer


class FeatureStoreManager:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

    def list(self) -> List[str]:
        raise NotImplementedError("FeatureStoreManager.list")
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_LIST)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        names = []
        lo, hi = 0, 8
        num_feature_stores = packer.unpack_uint64(data[lo:hi])
        for _ in range(num_feature_stores):
            lo, hi = hi, hi + 8
            feature_store_name_size = packer.unpack_uint64(data[lo:hi])
            lo, hi = hi, hi + feature_store_name_size
            names.append(packer.unpack_string(data[lo:hi]))
        return names

    def create(self, name: str, feature_size: int) -> None:
        raise NotImplementedError("FeatureStoreManager.create")
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_CREATE)
        msg += packer.pack_uint64(feature_size)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    def remove(self, name: str) -> None:
        raise NotImplementedError("FeatureStoreManager.remove")
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_REMOVE)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        self.client._send(msg)

        # Handle response
        self.client._recv()


class FeatureStore:
    def __init__(self, client: "MDBClient", name: str) -> None:
        self.client = client
        self.name = name
        self.feature_size = None

        self._feature_store_id = None
        self._closed = True
        self._open()

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._close()

    def __len__(self) -> int:
        return self.size()

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
        # TODO: Implement this
        raise NotImplementedError("FeatureStore.remove_tensor() is not implemented")

    @decorators.check_closed
    def get_tensor(self, node_id: int) -> List[float]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_GET_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.feature_size
        return packer.unpack_float_vector(data[lo:hi])

    def _open(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_OPEN)
        msg += packer.pack_uint64(len(self.name))
        msg += self.name.encode("utf-8")
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._feature_store_id = packer.unpack_uint64(data[0:8])
        self.feature_size = packer.unpack_uint64(data[8:16])
        self._closed = False

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
