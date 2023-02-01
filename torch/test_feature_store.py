from mdb_feature_store import MDBFeatureStore

import torch

feature_store = MDBFeatureStore()

num_papers = 100
num_paper_features = 400
paper_features = torch.rand(num_papers, num_paper_features)

num_authors = 50
num_author_features = 50
author_features = torch.rand(num_papers, num_paper_features)


# Add features
feature_store["paper", "x"] = paper_features
feature_store["author", "x"] = author_features

# Access features
assert torch.equal(feature_store["paper", "x", :], paper_features)
assert torch.equal(feature_store["paper"].x[10:20], paper_features[10:20])
assert torch.equal(feature_store["author", "x", 0:20], author_features[0:20])
