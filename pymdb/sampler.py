from typing import TYPE_CHECKING, List

from .protocol import RequestType
from .utils import packer
from .utils.graph import Graph

if TYPE_CHECKING:
    from .mdb_client import MDBClient

## Interface for generating samples from MillenniumDB.
#
# The MillenniumDB's server creates a new random seed after each initialization, so the
# results may vary between different runs.
class Sampler:
    ## Constructor.
    def __init__(self, client: "MDBClient"):
        ## Client instance.
        self.client = client

    def subgraph(self, num_seeds: int, num_neighbors: List[int]) -> Graph:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.SAMPLER_SUBGRAPH)
        msg += packer.pack_uint64(num_seeds)
        msg += packer.pack_uint64(len(num_neighbors))
        msg += packer.pack_uint64_vector(num_neighbors)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_graph(data)
    
    def subgraph_edge_existance(self, num_preseeds: int, num_neighbors: List[int]) -> Graph:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.SAMPLER_SUBGRAPH_EDGE_EXISTANCE)
        msg += packer.pack_uint64(num_preseeds)
        msg += packer.pack_uint64(len(num_neighbors))
        msg += packer.pack_uint64_vector(num_neighbors)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_graph(data)

    ## Returns at most `num_seeds` node ids for being used as seeds.
    def get_seeds(self, num_seeds: int) -> List[int]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.SAMPLER_GET_SEEDS)
        msg += packer.pack_uint64(num_seeds)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        seed_ids_size = packer.unpack_uint64(data[0:8])
        seed_ids = packer.unpack_uint64_vector(data[8 : 8 + 8 * seed_ids_size])
        return seed_ids
