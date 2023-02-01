from typing import Tuple

from mdb_feature_store import MDBFeatureStore
from mdb_graph_store import MDBGraphStore
from torch_geometric.sampler.base import BaseSampler, NodeSamplerInput, SamplerOutput

from torch import Tensor


class MDBSampler(BaseSampler):
    def __init__(self, data: Tuple[MDBFeatureStore, MDBGraphStore]):
        self.feature_store, self.graph_store = data

    def _sample(self, seed_nodes: Tensor) -> SamplerOutput:
        node = seed_nodes
        row = Tensor([i for i in range(node.size() - 1)])
        col = Tensor([i + 1 for i in range(node.size() - 1)])
        # Just return a dummy edge index for now.
        # This dummy connects each node to the next node in the sequence.
        # TODO: Use both stores to get the actual edge index, features, etc.
        return SamplerOutput(node=node, row=row, col=col)

    def sample_from_nodes(self, index: NodeSamplerInput) -> SamplerOutput:
        _, seed_nodes, _ = index
        return self._sample(seed_nodes)
