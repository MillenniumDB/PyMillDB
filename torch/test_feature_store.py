from mdb_feature_store import MDBFeatureStore, MDBTensorAttr
import torch

store = MDBFeatureStore()

tensor = torch.Tensor([1, 2, 3, 4, 5])
node_name = "Q123"

store[node_name] = tensor
assert torch.equal(store[node_name], tensor)

assert store.get_all_tensor_attrs() == [MDBTensorAttr(node_name)]
