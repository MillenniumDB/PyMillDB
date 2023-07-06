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


## MillenniumDB's Quad Model node representation in GraphWalker class
class WalkerNode(BuilderNode):
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
        properties: PropertiesDict = dict(),
    ):
        ## Source node name
        self.source = source
        ## Target node name
        self.target = target
        ## Edge type
        self.edge_type = edge_type
        ## Edge properties
        self.properties = properties

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source={self.source}, target={self.target}, edge_type={self.edge_type}, num_properties={len(self.properties)})"


## MillenniumDB's Quad Model edge representation in GraphWalker class.
#
# Note that the source and target nodes are identifiers rather than names
class WalkerEdge(BuilderEdge):
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


## Interface for walking across graphs in MillenniumDB
class GraphWalker:
    ## Constructor
    def __init__(self, client: "MDBClient"):
        ## Client instance
        self.client = client

    ## Describe a node by its identifier or name
    def get_node(self, node_id: int | str) -> WalkerNode:
        # Send request
        msg = b""
        if isinstance(node_id, int):
            msg += packer.pack_bool(True)
            msg += packer.pack_uint64(node_id)
        elif isinstance(node_id, str):
            msg += packer.pack_bool(False)
            msg += packer.pack_string(node_id)
        else:
            raise TypeError(f"node_id must be int or str, got {type(node_id)}")
        self.client._send(RequestType.GRAPH_WALKER_GET_NODE, msg)

        # Handle response
        data, _ = self.client._recv()
        # Name
        lo, hi = 0, data.index(b"\x00")
        name = packer.unpack_string(data, lo, hi)
        hi += 1
        # Labels
        lo, hi = hi, hi + 8
        num_labels = packer.unpack_uint64(data, lo, hi)
        labels = list()
        for _ in range(num_labels):
            lo, hi = hi, data.index(b"\x00", hi)
            label = packer.unpack_string(data, lo, hi)
            hi += 1
            labels.append(label)
        # Properties
        lo, hi = hi, hi + 8
        num_properties = packer.unpack_uint64(data, lo, hi)
        properties = dict()
        for _ in range(num_properties):
            # Key
            lo, hi = hi, data.index(b"\x00", hi)
            key = packer.unpack_string(data, lo, hi)
            hi += 1
            # Value
            value_type_code = data[hi]
            hi += 1
            if value_type_code == 1:
                # bool
                value = packer.unpack_bool(data, hi)
                hi += 1
            elif value_type_code == 2:
                # int64
                lo, hi = hi, hi + 8
                value = packer.unpack_int64(data, lo, hi)
            elif value_type_code == 3:
                # float
                lo, hi = hi, hi + 4
                value = packer.unpack_float(data, lo, hi)
            elif value_type_code == 4:
                # string
                lo, hi = hi, data.index(b"\x00", hi)
                value = packer.unpack_string(data, lo, hi)
                hi += 1
            else:
                raise ValueError(f"Invalid property value type code: {value_type_code}")
            properties[key] = value
        return WalkerNode(
            node_id=node_id, name=name, labels=labels, properties=properties
        )

    ## Get all outgoing or incoming edges from a node by its identifier or name
    def get_edges(
        self, node_id: int, direction: Literal["outgoing", "incoming"] = "outgoing"
    ) -> List[WalkerNode]:
        if direction not in ["outgoing", "incoming"]:
            raise ValueError('Direction must be either "outgoing" or "incoming".')

        # Send request
        msg = b""
        if isinstance(node_id, int):
            msg += packer.pack_bool(True)
            msg += packer.pack_uint64(node_id)
        elif isinstance(node_id, str):
            msg += packer.pack_bool(False)
            msg += packer.pack_string(node_id)
        else:
            raise TypeError(f"node_id must be int or str, got {type(node_id)}")
        self.client._send(RequestType.GRAPH_WALKER_GET_EDGES, msg)

        # Handle response
        data, _ = self.client._recv()

        edges = list()
        lo, hi = 0, 0
        while hi < len(data):
            lo, hi = hi, hi + 8
            source = packer.unpack_uint64(data, lo, hi)
            lo, hi = hi, hi + 8
            target = packer.unpack_uint64(data, lo, hi)
            lo, hi = hi, hi + 8
            edge_id = packer.unpack_uint64(data, lo, hi)
            lo, hi = hi, data.index(b"\x00", hi)
            edge_type = packer.unpack_string(data, lo, hi)
            hi += 1
            lo, hi = hi, hi + 8
            num_properties = packer.unpack_uint64(data, lo, hi)
            properties = dict()
            for _ in range(num_properties):
                # Key
                lo, hi = hi, data.index(b"\x00", hi)
                key = packer.unpack_string(data, lo, hi)
                hi += 1
                # Value
                value_type_code = data[hi]
                hi += 1
                if value_type_code == 1:
                    # bool
                    value = packer.unpack_bool(data, hi)
                    hi += 1
                elif value_type_code == 2:
                    # int64
                    lo, hi = hi, hi + 8
                    value = packer.unpack_int64(data, lo, hi)
                elif value_type_code == 3:
                    # float
                    lo, hi = hi, hi + 4
                    value = packer.unpack_float(data, lo, hi)
                elif value_type_code == 4:
                    # string
                    lo, hi = hi, data.index(b"\x00", hi)
                    value = packer.unpack_string(data, lo, hi)
                    hi += 1
                else:
                    raise ValueError(
                        f"Invalid property value type code: {value_type_code}"
                    )
                properties[key] = value
            edges.append(
                WalkerEdge(
                    source=source,
                    target=target,
                    edge_type=edge_type,
                    edge_id=edge_id,
                    propeties=properties,
                )
            )
        return edges
