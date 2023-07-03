import re
from typing import TYPE_CHECKING, Dict, List, Literal

from . import packer
from .protocol import RequestType

if TYPE_CHECKING:
    from .mdb_client import MDBClient

PropertiesDict = Dict[str, str | int | float | bool]


def dump_properties_milldb(properties: PropertiesDict) -> str:
    ret = ""
    for k, v in properties.items():
        ret += ""
        value_type = type(v)
        if value_type == str:
            ret += f' {k}:"{v}"'
        elif value_type in [int, float]:
            ret += f" {k}:{v}"
        elif value_type == bool:
            ret += f" {k}:{str(v).lower()}"
        else:
            print(
                f'Skipping property with type "{value_type}". Only str, int, float and bool are supported.'
            )
    return ret


## DataNode represents a MillenniumDB Quad Model node
class DataNode:
    def __init__(
        self,
        name: str,
        labels: List[str] = list(),
        properties: PropertiesDict = dict(),
        node_id: int = 0,
    ):
        self.name = name
        self.labels = labels
        self.properties = properties
        ## Has no effect in GraphBuilder as ids are generated when creating the database
        self.node_id = node_id

    def __repr__(self) -> str:
        return f"DataNode(name={self.name}, num_labels={len(self.labels)}, num_properties={len(self.properties)})"


## DataEdge represents a MillenniumDB Quad Model edge
class DataEdge:
    def __init__(
        self,
        source: str,
        target: str,
        edge_type: str,
        propeties: PropertiesDict = dict(),
        edge_id: int = 0,
    ):
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.properties = propeties
        ## Has no effect in GraphBuilder as ids are generated when creating the database
        self.edge_id = edge_id

    def __repr__(self) -> str:
        return f"DataEdge(source={self.source}, target={self.target}, type={self.edge_type}, num_properties={len(self.properties)})"


## Interface for building and dumping graphs in MillenniumDB's Quad Model format
#
# For more details on the format, see: https://github.com/MillenniumDB/MillenniumDB-Dev/blob/dev/doc/quad_model.md
class GraphBuilder:
    ## Constructor.
    def __init__(self):
        self._nodes: Dict[str, "DataNode"] = dict()
        self._edges: List["DataEdge"] = list()

    @property
    def nodes(self) -> List["DataNode"]:
        return list(self._nodes.values())

    @property
    def edges(self) -> List["DataEdge"]:
        return self._edges

    ## Add a node to the graph
    def add_node(self, node: "DataNode"):
        if node.name in self._nodes:
            raise ValueError(f'Node "{node.name}" already exists in the graph.')
        self._nodes[node.name] = node

    ## Add an edge to the graph
    def add_edge(self, edge: "DataEdge"):
        self._edges.append(edge)

    ## Dump the graph to a file in MillenniumDB's Quad Model format
    def dump_milldb(self, path: str) -> None:
        with open(path, "w") as f:
            for node in self.nodes:
                if not re.match("[a-zA-Z][a-zA-Z0-9_]*", str(node.name)):
                    print(
                        f'Skipping node. Identifier "{node.name}" does not match the pattern "[a-zA-Z][a-zA-Z0-9_]*".'
                    )
                    continue
                f.write(node.name)
                for label in node.labels:
                    f.write(f" :{label}")
                f.write(dump_properties_milldb(node.properties))
                f.write("\n")

            for edge in self.edges:
                if not re.match("[a-zA-Z][a-zA-Z0-9_]*", str(edge.source)):
                    print(
                        f'Skipping edge. Source identifier "{edge.source}" does not match the pattern "[a-zA-Z][a-zA-Z0-9_]*".'
                    )
                    continue
                elif not re.match("[a-zA-Z][a-zA-Z0-9_]*", str(edge.target)):
                    print(
                        f'Skipping edge. Target identifier "{edge.target}" does not match the pattern "[a-zA-Z][a-zA-Z0-9_]*".'
                    )
                    continue
                f.write(f"{edge.source}->{edge.target} :{edge.edge_type}")
                f.write(dump_properties_milldb(edge.properties))
                f.write("\n")

    def __repr__(self) -> str:
        return f"GraphBuilder(num_nodes={len(self.nodes)}, num_edges={len(self.edges)})"


## Interface for exploring graphs in MillenniumDB
class GraphExplorer:
    ## Constructor
    def __init__(self, client: "MDBClient"):
        ## Client instance
        self.client = client

    def get_edges(
        self, node_id: int, direction: Literal["outgoing", "incoming"] = "outgoing"
    ) -> List[DataEdge]:
        if direction not in ["outgoing", "incoming"]:
            raise ValueError('Direction must be either "outgoing" or "incoming".')

        # Send request
        msg = b""
        msg += packer.pack_uint64(node_id)
        msg += packer.pack_bool(direction == "outgoing")
        self.client._send(RequestType.GRAPH_EXPLORER_GET_EDGES, msg)

        # Handle response
        data, _ = self.client._recv()

        edges = list()
        for i in range(0, len(data), 4 * 8):
            edges.append(
                DataEdge(
                    source=packer.unpack_uint64(data[i : i + 8]),
                    target=packer.unpack_uint64(data[i + 8 : i + 16]),
                    edge_type=packer.unpack_uint64(data[i + 16 : i + 24]),
                    edge_id=packer.unpack_uint64(data[i + 24 : i + 32]),
                )
            )
        return edges
