from pymdb import BatchLoader, MDBClient

client = MDBClient()

batch_loader = BatchLoader(
    client,
    feature_store_name="random",
    num_seeds=10,
    batch_size=10,
    neighbor_sizes=[10, 10],
)

for batch in batch_loader:
    print(batch)
# batch_loader.close()

client.close()
