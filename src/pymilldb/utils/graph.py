from typing import List, Tuple


class Graph:
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
            f"Graph(num_seeds={self.num_seeds}, "
            f"node_ids=[{len(self.node_ids)}], "
            f"edge_ids=[{len(self.edge_ids)}], "
            f"edge_index=[{len(self.edge_index)}, 2])"
        )
