from mdb_feature_store import MDBFeatureStore
from mdb_graph_store import MDBGraphStore
from mdb_sampler import MDBSampler
from torch_geometric.loader import NodeLoader

import torch

feature_store = MDBFeatureStore()
graph_store = MDBGraphStore()


def create_db():
    # Dummy function to create a database.
    feature_store["person", "x"] = torch.tensor(
        [
            [0.1, 0.2, 0.3],
            [1.1, 1.2, 1.3],
            [2.1, 2.2, 2.3],
            [3.1, 3.2, 3.3],
            [4.1, 4.2, 4.3],
            [5.1, 5.2, 5.3],
        ],
        dtype=torch.float,
    )

    edge_index = torch.tensor(
        [
            [0, 1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1, 0],
        ],
        dtype=torch.long,
    )
    coo = edge_index.to_sparse_coo()
    graph_store["person_friend_person", "coo"] = coo


create_db()


node_sampler = MDBSampler(data=(feature_store, graph_store))

node_loader = NodeLoader(
    data=(feature_store, graph_store),
    node_sampler=node_sampler,
    input_nodes=torch.tensor([0, 1, 2], dtype=torch.long),
)

for batch in node_loader:
    print(batch)
