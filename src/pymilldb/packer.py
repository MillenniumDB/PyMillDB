import struct
from typing import List

from .sampler import GraphSample


def pack_byte(b: int) -> bytes:
    return struct.pack(">B", b)


def pack_bool(b: bool) -> bytes:
    return struct.pack(">?", b)


def pack_uint64(i: int) -> bytes:
    return struct.pack(">Q", i)


def pack_string(string: str) -> bytes:
    return pack_uint64(len(string)) + string.encode("utf-8")


def pack_uint64_vector(vector: List[int]) -> bytes:
    data = b""
    data += pack_uint64(len(vector))
    for value in vector:
        data += pack_uint64(value)
    return data


def pack_float_vector(vector: List[float]) -> bytes:
    data = b""
    data += pack_uint64(len(vector))
    for value in vector:
        data += struct.pack(">f", value)
    return data


def pack_string_vector(vector: List[str]) -> bytes:
    data = b""
    data += pack_uint64(len(vector))
    for value in vector:
        data += pack_string(value)
    return data


def unpack_bool(data: bytes, index: int) -> bool:
    return bool(data[index])


def unpack_uint64(data: bytes, start: int, end: int) -> int:
    return struct.unpack(">Q", data[start:end])[0]


def unpack_int64(data: bytes, start: int, end: int) -> int:
    return struct.unpack(">q", data[start:end])[0]


def unpack_float(data: bytes, start: int, end: int) -> float:
    return struct.unpack(">f", data[start:end])[0]


def unpack_string(data: bytes, start: int, end: int) -> str:
    return data[start:end].decode("utf-8")


def unpack_uint64_vector(data: bytes, start: int, end: int) -> List[int]:
    return [unpack_uint64(data, i, i + 8) for i in range(start, end, 8)]


def unpack_float_vector(data: bytes, start: int, end: int) -> List[float]:
    return [unpack_float(data, i, i + 4) for i in range(start, end, 4)]


def unpack_graph(data: bytes) -> "GraphSample":
    lo, hi = 0, 8
    num_seeds = unpack_uint64(data, lo, hi)
    lo, hi = hi, hi + 8
    num_nodes = unpack_uint64(data, lo, hi)
    lo, hi = hi, hi + 8
    num_edges = unpack_uint64(data, lo, hi)

    lo, hi = hi, hi + 8 * num_seeds
    seed_ids = unpack_uint64_vector(data, lo, hi)
    lo, hi = hi, hi + 8 * num_nodes
    node_ids = unpack_uint64_vector(data, lo, hi)
    lo, hi = hi, hi + 8 * num_edges
    edge_ids = unpack_uint64_vector(data, lo, hi)

    edge_index = [
        unpack_uint64_vector(data, i, i + 16)
        for i in range(hi, hi + 16 * num_edges, 16)
    ]
    return GraphSample(seed_ids, node_ids, edge_ids, edge_index)
