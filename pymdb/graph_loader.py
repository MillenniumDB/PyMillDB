# NOTE: The uint64 vectors are parsed as int64 vectors due the lack of the uint64 dtype
# in the torch.Tensor class.

import abc
from typing import TYPE_CHECKING, List

import torch

from .protocol import RequestType, StatusCode
from .utils import decorators, packer

if TYPE_CHECKING:
    from .mdb_client import MDBClient


## GraphLoader iterator output.
class Graph:
    def __init__(
        self,
        num_seeds: int,
        node_ids: List[int],
        edge_ids: List[List[int]],
        edge_index: torch.Tensor,
        node_features: torch.Tensor = None,
        edge_features: torch.Tensor = None,
        node_labels: List[List[int]] = None,
        edge_types: List[List[int]] = None,
    ):
        ## Number of seed nodes used to generate the graph.
        self.num_seeds = num_seeds
        ## Original node ids in the graph of shape [num_nodes].
        self.node_ids = node_ids
        ## Original edge ids in the graph of shape [num_edges].
        self.edge_ids = edge_ids
        ## Edge index of shape [2, num_edges].
        self.edge_index = edge_index

        if node_features is not None:
            ## Node features of shape [num_nodes, num_node_features].
            self.node_features = node_features
        if edge_features is not None:
            ## Edge features of shape [num_edges, num_edge_features].
            self.edge_features = edge_features
        if node_labels is not None:
            ## Node labels of shape [num_nodes, num_node_labels].
            self.node_labels = node_labels
        if edge_types is not None:
            ## Edge types of shape [num_edges].
            self.edge_types = edge_types

    def __repr__(self) -> str:
        res = "Graph("
        for k, v in self.__dict__.items():
            res += f"{k}="
            if isinstance(v, torch.Tensor):
                res += f"{list(v.shape)}, "
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], list):
                    res += f"[{len(v)}, {len(v[0])}], "
                else:
                    res += f"[{len(v)}], "
            else:
                res += f"{v}, "
        return res[:-2] + ")"


## Abstract class for the graph loader iterators.
class GraphLoader(abc.ABC):
    ## Constructor.
    @abc.abstractmethod
    def __init__(
        self,
        client: "MDBClient",
        batch_size: int,
        num_neighbors: List[int],
        node_feature_prop: str,
        edge_feature_prop: str,
        with_node_labels: bool,
        with_edge_types: bool,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        if len(num_neighbors) == 0:
            raise ValueError("num_neighbors must be non-empty")
        ## Client instance.
        self.client = client
        ## Number of seeds to use on each iteration.
        self.batch_size = batch_size
        ## Number of neighbors to sample at each layer (negative values are interpreted
        # as all neighbors).
        self.num_neighbors = list(
            map(lambda x: 2**64 - 1 if x < 0 else x, num_neighbors)
        )
        ## Property name of the node features. If empty, the node features are not sent.
        self.node_feature_prop = node_feature_prop
        ## Property name of the edge features. If empty, the edge features are not sent.
        self.edge_feature_prop = edge_feature_prop
        ## Whether to include the node labels in the graph.
        self.with_node_labels = with_node_labels
        ## Whether to include the edge labels in the graph.
        self.with_edge_types = with_edge_types

        self._graph_loader_id = None
        self._size = None
        self._closed = True

    @abc.abstractmethod
    def _new(self, *args) -> None:
        pass

    ## Returns `True` if the GraphLoader is closed.
    def is_closed(self) -> bool:
        return self._closed

    ## Closes the GraphLoader.
    def close(self) -> None:
        if not self._closed:
            self._close()

    ## Returns the number of graphs that can be generated by the instance.
    def __len__(self) -> int:
        return self.size()

    ## Returns the number of graphs that can be generated by the instance.
    @decorators.check_closed
    def size(self) -> int:
        return self._size

    ## Initializes the iterator.
    @decorators.check_closed
    def __iter__(self) -> "GraphLoader":
        self._begin()
        return self

    ## Returns the next graph. It is assumed that each 2D list is a matrix.
    @decorators.check_closed
    def __next__(self) -> dict:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.GRAPH_LOADER_NEXT)
        msg += packer.pack_uint64(self._graph_loader_id)
        self.client._send(msg)

        # Handle response
        data, code = self.client._recv()

        if code == StatusCode.END_OF_ITERATION:
            raise StopIteration

        res = dict()

        lo, hi = 0, 8
        num_nodes = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        num_edges = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        num_node_features = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        num_edge_features = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        num_node_labels = packer.unpack_uint64(data[lo:hi])

        lo, hi = hi, hi + 8
        res["num_seeds"] = packer.unpack_uint64(data[lo:hi])

        lo, hi = hi, hi + 8 * num_nodes
        res["node_ids"] = packer.unpack_uint64_vector(data[lo:hi])

        if self.node_feature_prop != "":
            lo, hi = hi, hi + 4 * num_node_features * num_nodes
            res["node_features"] = torch.tensor(
                data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
            ).reshape(num_nodes, num_node_features)

        if self.with_node_labels:
            res["node_labels"] = list()
            for _ in range(num_nodes):
                lo, hi = hi, hi + 8 * num_node_labels
                res["node_labels"].append(packer.unpack_uint64_vector(data[lo:hi]))

        lo, hi = hi, hi + 8 * num_edges
        res["edge_ids"] = packer.unpack_uint64_vector(data[lo:hi])

        if self.edge_feature_prop != "":
            lo, hi = hi, hi + 4 * num_edge_features * num_edges
            res["edge_features"] = torch.tensor(
                data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
            ).reshape(num_edges, num_edge_features)

        if self.with_edge_types:
            lo, hi = hi, hi + 8 * num_edges
            res["edge_types"] = packer.unpack_uint64_vector(data[lo:hi])

        lo, hi = hi, hi + 16 * num_edges
        res["edge_index"] = torch.tensor(
            data=packer.unpack_uint64_vector(data[lo:hi]), dtype=torch.int64
        ).reshape(2, num_edges)

        return Graph(**res)

    def _begin(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.GRAPH_LOADER_BEGIN)
        msg += packer.pack_uint64(self._graph_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.GRAPH_LOADER_CLOSE)
        msg += packer.pack_uint64(self._graph_loader_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self._graph_loader_id = None
        self._size = None
        self._closed = True


## GraphLoader for evaluation that performs mini-batching with the entire graph.
class EvalGraphLoader(GraphLoader):
    def __init__(
        self,
        client: "MDBClient",
        batch_size: int,
        num_neighbors: List[int],
        node_feature_prop: str,
        edge_feature_prop: str,
        with_node_labels: bool,
        with_edge_types: bool,
    ) -> None:
        super().__init__(
            client=client,
            batch_size=batch_size,
            num_neighbors=num_neighbors,
            node_feature_prop=node_feature_prop,
            edge_feature_prop=edge_feature_prop,
            with_node_labels=with_node_labels,
            with_edge_types=with_edge_types,
        )
        self._new()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.EVAL_GRAPH_LOADER_NEW)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(len(self.num_neighbors))
        msg += packer.pack_uint64(len(self.node_feature_prop))
        msg += packer.pack_uint64(len(self.edge_feature_prop))
        msg += packer.pack_bool(self.with_node_labels)
        msg += packer.pack_bool(self.with_edge_types)

        msg += packer.pack_uint64_vector(self.num_neighbors)
        msg += packer.pack_string(self.node_feature_prop)
        msg += packer.pack_string(self.edge_feature_prop)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._graph_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False


## GraphLoader that performs mini-batching sampling and generating a new set of seeds
# on each iterator initialization.
class SamplingGraphLoader(GraphLoader):
    def __init__(
        self,
        client: "MDBClient",
        batch_size: int,
        num_neighbors: List[int],
        node_feature_prop: str,
        edge_feature_prop: str,
        with_node_labels: bool,
        with_edge_types: bool,
        num_seeds: int,
    ) -> None:
        super().__init__(
            client=client,
            batch_size=batch_size,
            num_neighbors=num_neighbors,
            node_feature_prop=node_feature_prop,
            edge_feature_prop=edge_feature_prop,
            with_node_labels=with_node_labels,
            with_edge_types=with_edge_types,
        )
        if num_seeds == 0:
            raise ValueError("num_seeds must be greater than 0")
        ## Number of seed ids to generate.
        self.num_seeds = num_seeds
        self._new()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.SAMPLING_GRAPH_LOADER_NEW)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(self.num_seeds)
        msg += packer.pack_uint64(len(self.num_neighbors))
        msg += packer.pack_uint64(len(self.node_feature_prop))
        msg += packer.pack_uint64(len(self.edge_feature_prop))
        msg += packer.pack_bool(self.with_node_labels)
        msg += packer.pack_bool(self.with_edge_types)

        msg += packer.pack_uint64_vector(self.num_neighbors)
        msg += packer.pack_string(self.node_feature_prop)
        msg += packer.pack_string(self.edge_feature_prop)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._graph_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False


## GraphLoader that performs mini-batching sampling from a fixed set of seed ids.
class TrainGraphLoader(GraphLoader):
    def __init__(
        self,
        client: "MDBClient",
        batch_size: int,
        num_neighbors: List[int],
        node_feature_prop: str,
        edge_feature_prop: str,
        with_node_labels: bool,
        with_edge_types: bool,
        seed_ids: List[int],
    ) -> None:
        super().__init__(
            client=client,
            batch_size=batch_size,
            num_neighbors=num_neighbors,
            node_feature_prop=node_feature_prop,
            edge_feature_prop=edge_feature_prop,
            with_node_labels=with_node_labels,
            with_edge_types=with_edge_types,
        )
        if len(seed_ids) == 0:
            raise ValueError("seed_ids must be non-empty")
        ## List of seed ids to sample from.
        self.seed_ids = seed_ids
        self._new()

    def _new(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TRAIN_GRAPH_LOADER_NEW)
        msg += packer.pack_uint64(self.batch_size)
        msg += packer.pack_uint64(len(self.seed_ids))
        msg += packer.pack_uint64(len(self.num_neighbors))
        msg += packer.pack_uint64(len(self.node_feature_prop))
        msg += packer.pack_uint64(len(self.edge_feature_prop))
        msg += packer.pack_bool(self.with_node_labels)
        msg += packer.pack_bool(self.with_edge_types)

        msg += packer.pack_uint64_vector(self.seed_ids)
        msg += packer.pack_uint64_vector(self.num_neighbors)
        msg += packer.pack_string(self.node_feature_prop)
        msg += packer.pack_string(self.edge_feature_prop)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        self._graph_loader_id = packer.unpack_uint64(data[0:8])
        self._size = packer.unpack_uint64(data[8:16])
        self._closed = False
