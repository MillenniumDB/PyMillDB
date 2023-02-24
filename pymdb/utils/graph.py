import torch


class Graph:
    def __init__(
        self,
        node_features: torch.Tensor,  # [num_nodes, feature_size]
        node_labels: torch.Tensor,  # [num_nodes]
        edge_index: torch.Tensor,  # [2, num_edges]
    ) -> None:
        self.node_features = node_features
        self.node_labels = node_labels
        self.edge_index = edge_index

    def __eq__(self, other) -> bool:
        return (
            torch.equal(self.node_features, other.node_features)
            and torch.equal(self.node_labels, other.node_labels)
            and torch.equal(self.edge_index, other.edge_index)
        )

    def __repr__(self) -> str:
        return (
            "Graph("
            + f"node_features={list(self.node_features.shape)} "
            + f"node_labels={list(self.node_labels.shape)} "
            + f"edge_index={list(self.edge_index.shape)})"
        )
