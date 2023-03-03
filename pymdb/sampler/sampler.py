from typing import TYPE_CHECKING, List

from ..mdb_client.protocol import RequestType
from ..utils import packer

if TYPE_CHECKING:
    from ..mdb_client.mdb_client import MDBClient


class Sampler:
    def __init__(self, client: "MDBClient"):
        self.client = client

    def get_seed_ids(self, num_seeds: int) -> List[int]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.SAMPLER_GET_SEED_IDS)
        msg += packer.pack_uint64(num_seeds)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        seed_ids_size = packer.unpack_uint64(data[0:8])
        seed_ids = packer.unpack_uint64_vector(data[8 : 8 + 8 * seed_ids_size])
        return seed_ids
