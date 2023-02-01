from torch_geometric.sampler.base import (
    BaseSampler,
    NodeSamplerInput,
    SamplerOutput,
)


class MDBSampler(BaseSampler):
    def sample_from_nodes(index: NodeSamplerInput) -> SamplerOutput:
        """
        Performs sampling from the nodes specified in index.
        Returns a sampled subgraph in the specified output format.

        Args:
            index: The node indices to start sampling from.
        """
        raise NotImplementedError

    def sample_from_edges():
        """
        Not necessary for us
        """
        raise NotImplementedError
