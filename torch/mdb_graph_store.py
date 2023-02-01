from typing import Any, Dict, List, Optional, Tuple

from torch_geometric.data.graph_store import EdgeAttr, EdgeTensorType, GraphStore

from torch import Tensor

"""
This particular graph store abstraction makes a few key assumptions:
* The edge indices we care about storing are represented either in COO, CSC,
  or CSR format. They can be uniquely identified by an edge type (in PyG,
  this is a tuple of the source node, relation type, and destination node).
* Edge indices are static once they are stored in the graph. That is, we do not
  support dynamic modification of edge indices once they have been inserted
  into the graph store.
"""

"""
Examples:

* https://github.com/pyg-team/pytorch_geometric/blob/master/test/data/test_graph_store.py
* https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/testing/graph_store.py
"""


class MDBGraphStore(GraphStore):
    def __init__(self):
        super().__init__()
        self.store: Dict[tuple, Tuple[Tensor, Tensor]] = {}

    @staticmethod
    def key(attr: EdgeAttr) -> tuple:
        return (attr.edge_type, attr.layout.value, attr.is_sorted, attr.size)

    def _put_edge_index(self, edge_index: EdgeTensorType, edge_attr: EdgeAttr) -> bool:
        try:
            self.store[MDBGraphStore.key(edge_attr)] = edge_index
            return True
        except Exception as _:
            return False

    def _get_edge_index(self, edge_attr: EdgeAttr) -> Optional[EdgeTensorType]:
        try:
            return self.store[MDBGraphStore.key(edge_attr)]
        except Exception as _:
            return None

    def _remove_edge_index(self, edge_attr: EdgeAttr) -> bool:
        try:
            del self.store[edge_attr]
            return True
        except Exception as _:
            return False

    def get_all_edge_attrs(self) -> List[Any]:
        return [EdgeAttr(*key) for key in self.store.keys()]
