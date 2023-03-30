import struct
from typing import List


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
