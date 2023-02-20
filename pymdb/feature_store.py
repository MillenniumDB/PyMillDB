from typing import List

from .utils import decorators, packer


class FeatureStoreManager:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

    def list(self) -> List[str]:
        raise NotImplementedError("FeatureStoreManager.list() is not implemented")

    def create(self, name: str, feature_size: int) -> bool:
        raise NotImplementedError("FeatureStoreFactory.create() not implemented yet")

    def remove(self, name: str) -> bool:
        raise NotImplementedError("FeatureStore.delete() is not implemented")


class FeatureStore:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

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

        # TODO: Handle response
        raise NotImplementedError("FeatureStore.size() is not implemented")

    @decorators.check_closed
    def contains(self, node_id: int) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_CONTAINS)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)

        # TODO: Handle response
        raise NotImplementedError("FeatureStore.contains() is not implemented")

    @decorators.check_closed
    def insert_tensor(self, node_id: int, tensor: List[float]) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_INSERT_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)
        msg += packer.pack_uint64(len(tensor))
        msg += packer.pack_float_vector(tensor)

        # TODO: Handle response
        raise NotImplementedError("FeatureStore.insert_tensor() is not implemented")

    @decorators.check_closed
    def remove_tensor(self, node_id: int) -> bool:
        raise NotImplementedError("FeatureStore.remove_tensor() is not implemented")

    @decorators.check_closed
    def get_tensor(self, node_id: int) -> List[float]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_GET_TENSOR)
        msg += packer.pack_uint64(self._feature_store_id)
        msg += packer.pack_uint64(node_id)

        # TODO: Handle response
        raise NotImplementedError("FeatureStore.get_tensor() is not implemented")

    def _open(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_OPEN)
        msg += packer.pack_uint64(len(self.feature_store_name))
        msg += self.feature_store_name.encode("utf-8")

        # TODO: Handle response
        raise NotImplementedError("FeatureStore._open() is not implemented")

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.FEATURE_STORE_CLOSE)
        msg += packer.pack_uint64(self._feature_store_id)

        # TODO: Handle response
        raise NotImplementedError("FeatureStore._close() is not implemented")
