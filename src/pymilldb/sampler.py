from typing import TYPE_CHECKING, List, Tuple

from . import packer
from .protocol import RequestType

if TYPE_CHECKING:
    from .mdb_client import MDBClient

## GraphSample is the output of a sample.
class GraphSample:
    def __init__(
        self,
        seed_ids: List[int],
        node_ids: List[int],
        edge_ids: List[int],
        edge_index: List[Tuple[int, int]],
    ):
        self.num_seeds = len(seed_ids)
        self.node_ids = seed_ids + node_ids
        self.edge_ids = edge_ids
        self.edge_index = edge_index

    def __repr__(self) -> str:
        return (
            f"GraphSample(num_seeds={self.num_seeds}, "
            f"node_ids=[{len(self.node_ids)}], "
            f"edge_ids=[{len(self.edge_ids)}], "
            f"edge_index=[{len(self.edge_index)}, 2])"
        )

## Interface for generating samples from MillenniumDB.
#
# The MillenniumDB's server creates a new random seed after each initialization, so the
# results may vary between different runs.
class Sampler:
    ## Constructor.
    def __init__(self, client: "MDBClient"):
        ## Client instance.
        self.client = client

    ## Returns a random subgraph
    def subgraph(self, num_seeds: int, num_neighbors: List[int]) -> GraphSample:
        # Send request
        msg = b""
        msg += packer.pack_uint64(num_seeds)
        msg += packer.pack_uint64_vector(num_neighbors)
        self.client._send(RequestType.SAMPLER_SUBGRAPH, msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_graph(data)

    ## Returns a random subgraph for edge existance prediction
    def subgraph_edge_existance(
        self, num_preseeds: int, num_neighbors: List[int]
    ) -> GraphSample:
        # Send request
        msg = b""
        msg += packer.pack_uint64(num_preseeds)
        msg += packer.pack_uint64_vector(num_neighbors)
        self.client._send(RequestType.SAMPLER_SUBGRAPH_EDGE_EXISTANCE, msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_graph(data)
