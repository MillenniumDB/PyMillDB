from typing import List


class FeatureStoreFactory:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

    def create(self, name: str, feature_size: int) -> "FeatureStore" or None:
        raise NotImplementedError("FeatureStoreFactory.create() not implemented yet")

    def load(self, name: str) -> "FeatureStore" or None:
        raise NotImplementedError("FeatureStore.open() is not implemented")

    def remove(self, name: str) -> bool:
        raise NotImplementedError("FeatureStore.delete() is not implemented")


class FeatureStore:
    def __init__(self, client: "MDBClient") -> None:
        self.client = client

    def contains(self, node_id: int) -> bool:
        raise NotImplementedError("FeatureStore.contains() is not implemented")

    def insert_tensor(self, node_id: int, tensor: List[float]) -> bool:
        raise NotImplementedError("FeatureStore.insert_tensor() is not implemented")

    def remove_tensor(self, node_id: int) -> bool:
        raise NotImplementedError("FeatureStore.remove_tensor() is not implemented")

    def get_tensor(self, node_id: int) -> List[float]:
        raise NotImplementedError("FeatureStore.get_tensor() is not implemented")

    def size(self) -> int:
        raise NotImplementedError("FeatureStore.size() is not implemented")

    def __len__(self) -> int:
        return self.size()
