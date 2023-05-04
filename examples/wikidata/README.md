# Wikidata database generation

## Dataset

Download the dataset from https://figshare.com/s/50b7544ad6b1f51de060. It must be decompressed using a tool like `bzip2` for `linux`.

## MillenniumDB

1. Run `python3 nt_to_mdb_edges.py <source_file.nt> <destination_file.milldb>` for generating the edges.

2. Run `python3 mdb_edges_to_mdb_nodes.py <source_edges_file.milldb> <destination_nodes_file.milldb>` for generating the nodes and its features.

3. Run `python3 concat_files <edges_file.milldb> <nodes_file.milldb>` for appending the nodes to the edges file.