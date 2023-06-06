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

    # ts.size()
    # #ts["Q1"] = torch.tensor([2] * 10, dtype=torch.float32)
    # ts[2328696358397018112] = torch.tensor([2] * 10, dtype=torch.float32)
    # print("Write")
    # # print("Write", ts["Q1"])
    # 
    ts.close()
    print("Close")