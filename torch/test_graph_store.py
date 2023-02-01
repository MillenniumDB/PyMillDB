from mdb_graph_store import MDBGraphStore

import torch

graph_store = MDBGraphStore()

edge_index = torch.tensor(
    [
        [0, 1, 2, 3],
        [1300, 110, 4096, 12],
    ],
    dtype=torch.long,
)
coo = edge_index.to_sparse_coo()

# Put edges
graph_store["person_likes_movie", "coo"] = coo

# Access edges
print(graph_store["person_likes_movie", "coo"])
