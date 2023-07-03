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


## MillenniumDB's Quad Model node representation in GraphBuilder class
class BuilderNode:
    def __init__(
        self,
        name: str,
        labels: List[str] = list(),
        properties: PropertiesDict = dict(),
    ):
        ## Node name
        self.name: str = name
        ## Node labels
        self.labels: List[str] = labels
        ## Node properties
        self.properties: PropertiesDict = properties

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, num_labels={len(self.labels)}, num_properties={len(self.properties)})"


## MillenniumDB's Quad Model node representation in GraphExplorer class
class ExplorerNode(BuilderNode):
    def __init__(
        self,
        node_id: int,
        name: str,
        labels: List[str] = list(),
        properties: PropertiesDict = dict(),
    ):
        super().__init__(name, labels, properties)
        ## Node identifier
        self.node_id = node_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(node_id={self.node_id}, name={self.name}, num_labels={len(self.labels)}, num_properties={len(self.properties)})"


## MillenniumDB's Quad Model edge representation in GraphBuilder class
#
# Note that the source and target nodes are node names rather than identifiers
class BuilderEdge:
    def __init__(
        self,
        source: str,
        target: str,
        edge_type: str,
        propeties: PropertiesDict = dict(),
    ):
        ## Source node name
        self.source = source
        ## Target node name
        self.target = target
        ## Edge type
        self.edge_type = edge_type
        ## Edge properties
        self.properties = propeties

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source={self.source}, target={self.target}, edge_type={self.edge_type}, num_properties={len(self.properties)})"


## MillenniumDB's Quad Model edge representation in GraphExplorer class.
#
# Note that the source and target nodes are identifiers rather than names
class ExplorerEdge(BuilderEdge):
    def __init__(
        self,
        edge_id: int,
        source: int,
        target: int,
        edge_type: str,
        propeties: PropertiesDict = dict(),
    ):
        super().__init__(source, target, edge_type, propeties)
        ## Edge identifier
        self.edge_id = edge_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(edge_id={self.edge_id}, source={self.source}, target={self.target}, edge_type={self.edge_type}, num_properties={len(self.properties)})"


## Interface for building and dumping graphs in MillenniumDB's Quad Model format
#
# For more details on the format, see: https://github.com/MillenniumDB/MillenniumDB-Dev/blob/dev/doc/quad_model.md
class GraphBuilder:
    ## Constructor.
    def __init__(self):
        self._nodes: Dict[str, BuilderNode] = dict()
        self._edges: List[BuilderEdge] = list()

    @property
    def nodes(self) -> List[BuilderNode]:
        return list(self._nodes.values())

    @property
    def edges(self) -> List[BuilderEdge]:
        return self._edges

    ## Add a node to the graph
    def add_node(self, node: BuilderNode):
        if node.name in self._nodes:
            raise ValueError(f'Node "{node.name}" already exists in the graph.')
        self._nodes[node.name] = node

    ## Add an edge to the graph
    def add_edge(self, edge: BuilderEdge):
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
        return f"{self.__class__.__name__}(num_nodes={len(self.nodes)}, num_edges={len(self.edges)})"


## Interface for exploring graphs in MillenniumDB
class GraphExplorer:
    ## Constructor
    def __init__(self, client: "MDBClient"):
        ## Client instance
        self.client = client

    def get_node(self, node_id: int) -> ExplorerNode:
        # Send request
        msg = b""
        msg += packer.pack_uint64(node_id)
        self.client._send(RequestType.GRAPH_EXPLORER_GET_NODE, msg)

        # Handle response
        data, _ = self.client._recv()

        name = packer.unpack_string(data)
        labels = list()
        lo = len(name) + 1 # +1 for the null terminator
        while lo < len(data):
            label = packer.unpack_string(data[lo : ])
            labels.append(label)
            lo += len(label) + 1 # +1 for the null terminator
        return ExplorerNode(node_id=node_id, name=name, labels=labels)

    def get_edges(
        self, node_id: int, direction: Literal["outgoing", "incoming"] = "outgoing"
    ) -> List[ExplorerEdge]:
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
        lo = 0
        while lo < len(data):
            source = packer.unpack_uint64(data[lo : lo + 8])
            target = packer.unpack_uint64(data[lo + 8 : lo + 16])
            edge_id = packer.unpack_uint64(data[lo + 16 : lo + 24])
            edge_type = packer.unpack_string(data[lo + 24 :])
            edges.append(
                ExplorerEdge(
                    source=source,
                    target=target,
                    edge_type=edge_type,
                    edge_id=edge_id,
                )
            )
            lo += 24 + len(edge_type) + 1 # +1 for the null terminator
        return edges
