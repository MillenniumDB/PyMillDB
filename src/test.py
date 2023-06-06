import torch

from pymilldb import MDBClient, TensorStore

with MDBClient() as client:
    if TensorStore.exists(client, "test"):
        print("Exists")
        TensorStore.remove(client, "test")
        print("Remove")
    else:
        print("Does not exists")

    TensorStore.create(client, "test", 10)
    print("Create")

    ts = TensorStore(client, "test")
    print("Open", ts.name, ts.tensor_size)

    if "xd" in ts:
        print("xd in ts")
    else:
        print("xd not in ts")

    print("now the size is: ", ts.size())
    ts["Q1"] = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=torch.float32)
    ts["Q2"] = torch.tensor([1] * 10, dtype=torch.float)
    ts[2328696358397018112] = torch.tensor([99] * 10, dtype=torch.float32)  # same as Q1
    print("stored value for Q1:", ts["Q1"])
    print("stored value for Q2:", ts["Q2"])
    print("now the size is: ", ts.size())

    print("multi_get:", ts[["Q1", "Q2"]])

    ts[["Q1", "Q2"]] = torch.tensor([3] * 20, dtype=torch.float32).reshape(2, 10)
    print("after multi_insert:", ts[["Q1", "Q2"]])

    ts.close()
    print("Close")
