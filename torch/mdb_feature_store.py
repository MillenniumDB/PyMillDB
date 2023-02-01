from typing import Dict, List, Optional

from torch_geometric.data.feature_store import FeatureStore, TensorAttr, _field_status
from torch_geometric.typing import FeatureTensorType

from torch import Tensor

"""
This particular feature store abstraction makes a few key assumptions:
* The features we care about storing are node and edge features of a graph.
  To this end, the attributes that the feature store supports include a
  `group_name` (e.g. a heterogeneous node name or a heterogeneous edge type),
  an `attr_name` (e.g. `x` or `edge_attr`), and an index.
* A feature can be uniquely identified from any associated attributes specified
  in `TensorAttr`.

Source: https://pytorch-geometric.readthedocs.io/en/latest/_modules/torch_geometric/data/feature_store.html
"""

"""
Notes:

* torch.Tensor types : https://pytorch.org/docs/stable/tensor_attributes.html
* update_tensor      : Can be implemented for better performance.
* _multi_get_tensor  : Can be implemented for better performance.
"""

"""
Examples:

* https://github.com/pyg-team/pytorch_geometric/blob/master/test/data/test_feature_store.py
* https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/testing/feature_store.py
"""


class MDBTensorAttr(TensorAttr):
    def __init__(self, group_name: str = _field_status.UNSET):
        # For now, we support only a `group_name`.
        # Feature tensors are stored in a key-value store where the key is the name of
        # the node.
        super().__init__(group_name, None, None)


class MDBFeatureStore(FeatureStore):
    def __init__(self):
        super().__init__(MDBTensorAttr)
        self.store: Dict[str, Tensor] = {}

    @staticmethod
    def key(attr: TensorAttr) -> str:
        return attr.group_name

    def _put_tensor(self, tensor: FeatureTensorType, attr: TensorAttr) -> bool:
        try:
            self.store[MDBFeatureStore.key(attr)] = tensor
            return True
        except Exception as _:
            return False

    def _get_tensor(self, attr: TensorAttr) -> Optional[FeatureTensorType]:
        try:
            return self.store[MDBFeatureStore.key(attr)]
        except Exception as _:
            return None

    def _remove_tensor(self, attr: TensorAttr) -> bool:
        try:
            del self.store[MDBFeatureStore.key(attr)]
            return True
        except Exception as _:
            return False

    def _get_tensor_size(self, attr: TensorAttr) -> Optional[int]:
        try:
            return self.store[MDBFeatureStore.key(attr)].size()
        except Exception as _:
            return None

    def get_all_tensor_attrs(self) -> List[TensorAttr]:
        return [self._tensor_attr_cls(key) for key in self.store.keys()]

    def __len__(self) -> int:
        return len(self.store)
