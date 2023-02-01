from mdb_graph_store import MDBGraphStore

import torch

graph_store = MDBGraphStore()

edge_index = torch.tensor(
    [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
    ],
    dtype=torch.long,
)
coo = edge_index.to_sparse_coo()

# Put edges
graph_store["person_friend_person", "coo"] = coo

# Access edges
print(graph_store["person_friend_person", "coo"])
