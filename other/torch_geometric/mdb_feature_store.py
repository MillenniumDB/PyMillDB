from typing import Dict, List, Optional, Tuple

from torch_geometric.data.feature_store import FeatureStore, TensorAttr
from torch_geometric.typing import FeatureTensorType

import torch
from torch import Tensor

"""
This particular feature store abstraction makes a few key assumptions:
* The features we care about storing are node and edge features of a graph.
  To this end, the attributes that the feature store supports include a
  `group_name` (e.g. a heterogeneous node name or a heterogeneous edge type),
  an `attr_name` (e.g. `x` or `edge_attr`), and an index.
* A feature can be uniquely identified from any associated attributes specified
  in `TensorAttr`.

Useful links:
* https://github.com/pyg-team/pytorch_geometric/blob/master/test/data/test_feature_store.py
* https://github.com/pyg-team/pytorch_geometric/blob/master/torch_geometric/testing/feature_store.py
* https://pytorch-geometric.readthedocs.io/en/latest/_modules/torch_geometric/data/feature_store.html
"""


class MDBFeatureStore(FeatureStore):
    def __init__(self):
        super().__init__()
        self.store: Dict[Tuple[str, str], Tuple[Tensor, Tensor]] = {}

    @staticmethod
    def key(attr: TensorAttr) -> Tuple[str, str]:
        return (attr.group_name, attr.attr_name)

    def _put_tensor(self, tensor: FeatureTensorType, attr: TensorAttr) -> bool:
        try:
            index = attr.index
            if not attr.is_set("index") or index is None:
                index = torch.arange(0, tensor.shape[0])
            self.store[MDBFeatureStore.key(attr)] = (index, tensor)
            return True
        except Exception as _:
            return False

    def _get_tensor(self, attr: TensorAttr) -> Optional[FeatureTensorType]:
        try:
            _, tensor = self.store.get(MDBFeatureStore.key(attr), (None, None))
            if tensor is None:
                return None
            elif attr.index is None:
                return tensor
            elif isinstance(attr.index, slice) and attr.index == slice(None):
                return tensor
            return tensor[attr.index]

        except Exception as _:
            return None

    def _remove_tensor(self, attr: TensorAttr) -> bool:
        try:
            del self.store[MDBFeatureStore.key(attr)]
            return True
        except Exception as _:
            return False

    def _get_tensor_size(self, attr: TensorAttr) -> Optional[Tuple[int]]:
        try:
            return self._get_tensor(attr).size()
        except Exception as _:
            return None

    def get_all_tensor_attrs(self) -> List[TensorAttr]:
        return [self._tensor_attr_cls(*key) for key in self.store.keys()]

    def __len__(self) -> int:
        return len(self.store)
