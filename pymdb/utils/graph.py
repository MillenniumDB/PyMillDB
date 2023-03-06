from typing import List

import torch


class Graph:
    def __init__(
        self,
        node_features: torch.Tensor,  # [num_nodes, feature_size]
        node_labels: torch.Tensor,  # [num_nodes]
        edge_index: torch.Tensor,  # [2, num_edges]
        seed_ids: List[int],  # [num_seeds]
    ) -> None:
        self.node_features = node_features
        self.node_labels = node_labels
        self.edge_index = edge_index
        self.seed_ids = seed_ids

    def __repr__(self) -> str:
        return (
            "Graph("
            + f"node_features={list(self.node_features.shape)}, "
            + f"node_labels={list(self.node_labels.shape)}, "
            + f"edge_index={list(self.edge_index.shape)}, "
            + f"seed_ids=[{len(self.seed_ids)}])"
        )
