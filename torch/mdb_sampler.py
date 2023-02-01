from typing import Tuple

from mdb_feature_store import MDBFeatureStore
from mdb_graph_store import MDBGraphStore
from torch_geometric.sampler.base import (
    BaseSampler,
    EdgeSamplerInput,
    NodeSamplerInput,
    SamplerOutput,
)

from torch import Tensor

"""
Note:
* MDBSampler must know how to sample on MDBGraphStore
"""


class MDBSampler(BaseSampler):
    def __init__(self, data: Tuple[MDBFeatureStore, MDBGraphStore]):
        self.feature_store, self.graph_store = data

    def _sample(self, seed_nodes: Tensor) -> SamplerOutput:
        node = seed_nodes
        print(node)
        row = Tensor([i for i in range(node.size() - 1)])
        col = Tensor([i + 1 for i in range(node.size() - 1)])
        # Just return a dummy edge index for now.
        # This dummy connects each node to the next node in the sequence.
        # TODO: Use both stores to get the actual edge index, features, etc.
        return SamplerOutput(node=node, row=row, col=col)

    def sample_from_nodes(self, index: NodeSamplerInput) -> SamplerOutput:
        print(index)
        _, seed_nodes, _ = index
        # return self._sample(seed_nodes)
        return SamplerOutput(
            node=seed_nodes,
            row=Tensor([0]),
            col=Tensor([1]),
            edge=None,
            batch=None,
            metadata=None,
        )

    def sample_from_edges(self, index: EdgeSamplerInput) -> SamplerOutput:
        raise NotImplementedError
