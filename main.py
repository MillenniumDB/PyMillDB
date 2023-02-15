from pymdb import BatchLoader, MDBClient

client = MDBClient()

batch_loader = BatchLoader(
    client,
    feature_store_name="test",
    num_seeds=10,
    batch_size=10,
    neighbor_sizes=[10, 10],
)

client.close()
