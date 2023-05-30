import struct
from typing import List

from .graph import Graph


def pack_byte(b: int) -> bytes:
    return struct.pack(">B", b)


def pack_bool(b: bool) -> bytes:
    return struct.pack(">?", b)


def pack_uint64(i: int) -> bytes:
    return struct.pack(">Q", i)


def pack_string(string: str) -> bytes:
    return string.encode("utf-8")


def pack_uint64_vector(vector: List[int]) -> bytes:
    data = b""
    for value in vector:
        data += pack_uint64(value)
    return data


def pack_float_vector(vector: List[float]) -> bytes:
    data = b""
    for value in vector:
        data += struct.pack(">f", value)
    return data


def unpack_bool(data: bytes) -> bool:
    return struct.unpack(">?", data)[0]


def unpack_uint64(data: bytes) -> int:
    return struct.unpack(">Q", data)[0]


def unpack_float(data: bytes) -> float:
    return struct.unpack(">f", data)[0]


def unpack_string(data: bytes) -> str:
    return data.decode("utf-8")


def unpack_uint64_vector(data: bytes) -> List[int]:
    return [unpack_uint64(data[i : i + 8]) for i in range(0, len(data), 8)]


def unpack_float_vector(data: bytes) -> List[float]:
    return [unpack_float(data[i : i + 4]) for i in range(0, len(data), 4)]


def unpack_graph(data: bytes) -> Graph:
    lo, hi = 0, 8
    num_seeds = unpack_uint64(data[lo:hi])
    lo, hi = hi, hi + 8
    num_nodes = unpack_uint64(data[lo:hi])
    lo, hi = hi, hi + 8
    num_edges = unpack_uint64(data[lo:hi])

    lo, hi = hi, hi + 8 * num_seeds
    seed_ids = unpack_uint64_vector(data[lo:hi])
    lo, hi = hi, hi + 8 * num_nodes
    node_ids = unpack_uint64_vector(data[lo:hi])
    lo, hi = hi, hi + 8 * num_edges
    edge_ids = unpack_uint64_vector(data[lo:hi])

    edge_index = list()
    for _ in range(num_edges):
        lo, hi = hi, hi + 16
        edge_index.append(unpack_uint64_vector(data[lo:hi]))
    return Graph(seed_ids, node_ids, edge_ids, edge_index)
