import struct
from typing import List


def pack_byte(b: int) -> bytes:
    return struct.pack(">B", b)


def pack_uint64(i: int) -> bytes:
    return struct.pack(">Q", i)


def unpack_uint64(data: bytes) -> int:
    return struct.unpack(">Q", data)[0]


def pack_string(string: str) -> bytes:
    return string.encode("utf-8")


def unpack_uint64_vector(data: bytes) -> List[int]:
    vector = []
    for i in range(0, len(data), 8):
        vector.append(unpack_uint64(data[i : i + 8]))
    return vector
