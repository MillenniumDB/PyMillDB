from typing import List

from .protocol import RequestType


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

    def _new(self) -> None:
        # Send BATCH_LOADER_NEW request
        msg = RequestType.BATCH_LOADER_NEW.value
        msg += self.num_seeds.to_bytes(8, "little")
        msg += self.batch_size.to_bytes(8, "little")
        msg += len(self.neighbor_sizes).to_bytes(8, "little")
        msg += len(self.feature_store_name).to_bytes(8, "little")
        for neighbor_size in self.neighbor_sizes:
            msg += neighbor_size.to_bytes(8, "little")
        msg += self.feature_store_name.encode("utf-8")
        self.client._send(msg)

        # TODO: Receive BATCH_LOADER_NEW response
        response = self.client._recv(9)
        print("response:", response)
        raise NotImplementedError("BatchLoader._new() not implemented yet")

    def next(self) -> "Graph":
        # Send BATCH_LOADER_NEXT request
        msg = RequestType.BATCH_LOADER_NEXT.value
        msg += self._batch_loader_id
        self.client._send(msg)

        # TODO: Receive BATCH_LOADER_NEXT response
        raise NotImplementedError("BatchLoader.next() not implemented yet")
        # TODO: Return Graph

    def close(self) -> None:
        # Send BATCH_LOADER_CLOSE request
        msg = RequestType.BATCH_LOADER_CLOSE.value
        msg += self._batch_loader_id
        self.client._send(msg)

        # TODO: Receive BATCH_LOADER_CLOSE response
        raise NotImplementedError("BatchLoader.close() not implemented yet")
        self._closed = True

    def __repr__(self) -> str:
        return (
            "BatchLoader("
            + f"feature_store_name={self.feature_store_name}, "
            + f"num_seeds={self.num_seeds}, "
            + f"batch_size={self.batch_size}, "
            + f"neighbor_sizes={self.neighbor_sizes})"
        )
