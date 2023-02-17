import numpy as np


class Graph:
    def __init__(
        self,
        node_features: np.ndarray,
        node_labels: np.ndarray,
        edge_index: np.ndarray,
    ):
        self.node_features = node_features
        self.node_labels = node_labels
        self.edge_index = edge_index

    def __repr__(self) -> str:
        return (
            "Graph(node_features="
            + str(self.node_features.shape)
            + " node_labels="
            + str(self.node_labels.shape)
            + " edge_index="
            + str(self.edge_index.shape)
            + ")"
        )
