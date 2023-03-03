import torch


class Graph:
    def __init__(
        self,
        node_features: torch.Tensor,  # [num_nodes, feature_size]
        node_labels: torch.Tensor,  # [num_nodes]
        edge_index: torch.Tensor,  # [2, num_edges]
        num_seeds: int,  # Number of seed nodes used to build the subgraph. They are assumed to be the first num_seeds nodes.
    ) -> None:
        self.node_features = node_features
        self.node_labels = node_labels
        self.edge_index = edge_index
        self.num_seeds = num_seeds

    def __repr__(self) -> str:
        return (
            "Graph("
            + f"node_features={list(self.node_features.shape)}, "
            + f"node_labels={list(self.node_labels.shape)}, "
            + f"edge_index={list(self.edge_index.shape)}, "
            + f"num_seeds={self.num_seeds})"
        )
