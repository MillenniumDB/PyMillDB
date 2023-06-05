import torch

from pymilldb import MDBClient, TensorStore

with MDBClient() as client:
    if TensorStore.exists(client, "test"):
        print("Exists")
        TensorStore.remove(client, "test")
        print("Remove")

    TensorStore.create(client, "test", 10)
    print("Create")

    ts = TensorStore(client, "test")
    print("Open", ts.name, ts.tensor_size, ts.size())

    ts["Q1"] = torch.tensor([1] * 10, dtype=torch.float32)
    print("Write")
    # print("Write", ts["Q1"])

    ts.close()
    print("Close")