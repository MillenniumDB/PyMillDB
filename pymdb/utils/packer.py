import struct
from typing import List, Tuple

import numpy as np


def pack_byte(b: int) -> bytes:
    return struct.pack(">B", b)


def pack_uint64(i: int) -> bytes:
    return struct.pack(">Q", i)


def pack_string(string: str) -> bytes:
    return string.encode("utf-8")


def pack_uint64_vector(vector: List[int]) -> bytes:
    data = b""
    for value in vector:
        data += pack_uint64(value)
    return data


def unpack_uint64(data: bytes) -> int:
    return struct.unpack(">Q", data)[0]


def unpack_uint64_vector(data: bytes, shape: int or Tuple[int] = -1) -> np.ndarray:
    return np.frombuffer(data, dtype=">Q").reshape(shape)


def unpack_float_vector(data: bytes, shape: int or Tuple[int] = -1) -> np.ndarray:
    return np.frombuffer(data, dtype=np.float32).reshape(shape)
