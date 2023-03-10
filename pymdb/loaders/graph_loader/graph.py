from typing import List

import torch


class Graph:
    def __init__(
        self,
        node_features: torch.Tensor,  # [num_nodes, feature_size]
        node_labels: torch.Tensor,  # [num_nodes]
        edge_index: torch.Tensor,  # [2, num_edges]
        node_ids: List[int],  # [num_nodes]
        num_seeds: int,
        feature_size: int,
    ) -> None:
        self.node_features = node_features
        self.node_labels = node_labels
        self.edge_index = edge_index
        self.node_ids = node_ids
        self.num_seeds = num_seeds
        self.feature_size = feature_size

    def __repr__(self) -> str:
        return (
            "Graph("
            + f"node_features={list(self.node_features.shape)}, "
            + f"node_labels={list(self.node_labels.shape)}, "
            + f"edge_index={list(self.edge_index.shape)}, "
            + f"node_ids=[{len(self.node_ids)}], "
            + f"num_seeds={self.num_seeds}, "
            + f"feature_size={self.feature_size})"
        )
