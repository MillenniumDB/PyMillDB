from typing import Any, Optional, Union, List

import torch
import numpy as np
from torch_geometric.data.feature_store import FeatureStore


"""
Notes:

- torch.Tensor types : https://pytorch.org/docs/stable/tensor_attributes.html
- update_tensor      : Can be implemented for better performance.
- _multi_get_tensor  : Can be implemented for better performance.
- Must review the id type. Currently it is Any, but it should be a TensorAttr.
"""


class MDBFeatureStore(FeatureStore):
    def _put_tensor(tensor: Union[torch.Tensor, np.ndarray], id: Any) -> bool:
        """
        Synchronously put a tensor into the feature store.
        Returns whether insertion was successful.

        Args:
            tensor: The feature tensor to be added.
            id: An unique identifier for the tensor.
        """
        pass

    def _get_tensor(id: Any) -> Optional[torch.Tensor]:
        """
        Synchronously get a tensor from the feature store.
        Returns the tensor if it exists, None otherwise.

        Args:
            id: An unique identifier for the tensor.
        """
        pass

    def _remove_tensor(self, id: Any) -> bool:
        """
        Synchronously remove a tensor from the feature store.
        Returns whether removal was successful.

        Args:
            id: An unique identifier for the tensor.
        """
        pass

    def _get_tensor_size(self, id: Any) -> Optional[int]:
        """
        Returns the size of the tensor if it exists, None otherwise.

        Args:
            id: An unique identifier for the tensor.
        """
        pass

    def get_all_tensor_attrs(self) -> List[Any]:
        """
        Returns a list of all tensor ids from the feature store.
        """
        pass

    def __len__(self) -> int:
        """
        Returns the number of tensors in the feature store.
        """
        pass