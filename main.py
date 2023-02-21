from pymdb import BatchLoader, MDBClient

with MDBClient(host="127.0.0.1", port=8080) as client:
    batch_loader = BatchLoader(
        client,
        feature_store_name="random",
        num_seeds=30,
        batch_size=10,
        neighbor_sizes=[2, 2],
        seed=2023,
    )

    print(batch_loader)
    for batch in batch_loader:
        print(batch)
