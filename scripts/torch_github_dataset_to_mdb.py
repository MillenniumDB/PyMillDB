# This script converts the GitHub dataset from PyTorch Geometric to the MillenniumDB
# format and creates a database from it.

import os
import subprocess

from torch_geometric.datasets import GitHub

CREATE_DB_PATH = "/home/zeus/MillenniumDB-Dev/build/Release/bin/create_db"
DESTINATION_PATH = "/home/zeus/MillenniumDB-Dev/tests/dbs/github/"

# Download the dataset
dataset = GitHub(root="/tmp/")
data = dataset[0]
# Write the graph data to the MillenniumDB format on a temporary file
with open("github.tmp", "w") as f:
    for node_id, label in enumerate(data.y):
        f.write(f'dev{node_id} :{"web" if label == 0 else "ai"}\n')
    for edge in data.edge_index.t().tolist():
        f.write(f"dev{edge[0]}->dev{edge[1]} :follow\n")

# Create the graph database
create_db = subprocess.run(
    [CREATE_DB_PATH, "github.tmp", DESTINATION_PATH], capture_output=True
)

# Remove the temporary file
os.remove("github.tmp")

# Check if the database was created successfully
if create_db.returncode != 0:
    print("Error on create_db:", create_db.stderr.decode("utf-8").strip())
    exit(1)
