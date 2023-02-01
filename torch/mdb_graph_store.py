from typing import Any, Optional, Tuple, List
import torch
from torch_geometric.data.graph_store import GraphStore

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
Notes:

* Must review the id type. Currently it is Any, but it should be a EdgeAttr.
"""

"""
Examples:

* https://github.com/pyg-team/pytorch_geometric/blob/master/test/data/test_graph_store.py
* https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/testing/graph_store.py
"""


class MDBGraphStore(GraphStore):
    def _put_edge_index(edge_index: Tuple[torch.Tensor, torch.Tensor]) -> bool:
        """
        Synchronously put an edge index into the graph store.}
        Returns whether the insertion was successful.

        Args:
            edge_index: The edge index to be added. (CSC format*)
        """
        raise NotImplementedError

    def _get_edge_index(self, id: Any) -> Optional[Tuple[torch.Tensor, torch.Tensor]]:
        """
        Synchronously get an edge index from the graph store.
        Returns the edge index if it exists, None otherwise.

        Args:
            id: An unique identifier for the edge index.
        """
        raise NotImplementedError

    def _remove_edge_index(self, id: Any) -> bool:
        """
        Synchronously remove an edge index from the graph store.
        Returns whether removal was successful.

        Args:
            id: An unique identifier for the edge index.
        """
        raise NotImplementedError

    def get_all_edge_attrs(self) -> List[Any]:
        """
        Returns all edge attributes from the graphstore.
        """
        raise NotImplementedError
