from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .mdb_client import MDBClient

from .feature_store import FeatureStore
from .protocol import RequestType
from .utils import packer


class FeatureStoreManager:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

    def open(self, name: str) -> "FeatureStore":
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_OPEN)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 8
        feature_store_id = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        feature_size = packer.unpack_uint64(data[lo:hi])
        return FeatureStore(self.client, name, feature_store_id, feature_size)

    def list(self) -> List[str]:
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
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_REMOVE)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        self.client._send(msg)

        # Handle response
        self.client._recv()
