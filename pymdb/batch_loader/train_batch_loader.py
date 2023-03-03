from typing import TYPE_CHECKING, List

from ..mdb_client.protocol import RequestType
from ..utils import packer
from .batch_loader import BatchLoader

if TYPE_CHECKING:
    from ..mdb_client.mdb_client import MDBClient


class TrainBatchLoader(BatchLoader):
    def __init__(
        self,
        client: "MDBClient",
        feature_store_name: str,
        batch_size: int,
        num_neighbors: List[int],
        seed_ids: List[int],
    ) -> None:
        self.client = client
        self.feature_store_name = feature_store_name
        self.batch_size = batch_size
        # Convert negative values to max uint64 value
        self.num_neighbors = list(
            map(lambda x: 2**64 - 1 if x < 0 else x, num_neighbors)
        )
        self.seed_ids = seed_ids

        self._batch_loader_id = None
        self._size = None
        self._closed = True
        self._new()
        self._begin()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TRAIN_BATCH_LOADER_NEW)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(len(self.num_neighbors))
        msg += packer.pack_uint64(len(self.feature_store_name))
        msg += packer.pack_uint64(len(self.seed_ids))
        # TODO: Convert negative values to UINT64_MAX
        msg += packer.pack_uint64_vector(self.num_neighbors)
        msg += packer.pack_string(self.feature_store_name)
        msg += packer.pack_uint64_vector(self.seed_ids)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._batch_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}(batch_size="{self.feature_store_name}", '
            + f"num_neighbors={self.num_neighbors}, "
            + f'feature_store_name="{self.feature_store_name}", '
            + f"num_seed_ids={len(self.seed_ids)})"
        )
