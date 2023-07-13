from collections.abc import Iterable
from typing import TYPE_CHECKING, List, Union

import torch

from . import decorators, packer
from .protocol import RequestType

if TYPE_CHECKING:
    from .mdb_client import MDBClient


## Interface for storing tensors in the MillenniumDB's TensorStore.
#
# TensorStore is a key-value store where the key is a `(uint64 object_id)` and the value is
# a `(vector<float> tensor)`. The tensor size is fixed and is specified when the store is
# created. For consistency and our own use cases the tensors cannot be removed.
class TensorStore:
    ## Returns `True` if the store exists.
    @staticmethod
    def exists(client: "MDBClient", name: str) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_string(name)
        client._send(RequestType.TENSOR_STORE_EXISTS, msg)

        # Handle response
        data, _ = client._recv()
        return packer.unpack_bool(data, 0)

    ## Creates a new store on disk.
    @staticmethod
    def create(client: "MDBClient", name: str, tensor_size: int) -> None:
        if tensor_size <= 0:
            raise ValueError(f"tensor_size must be positive integer, got {tensor_size}")
        # Send request
        msg = b""
        msg += packer.pack_uint64(tensor_size)
        msg += packer.pack_string(name)
        client._send(RequestType.TENSOR_STORE_CREATE, msg)

        # Handle response
        client._recv()

    ## Removes a store from disk.
    @staticmethod
    def remove(client: "MDBClient", name: str) -> None:
        # Send request
        msg = b""
        msg += packer.pack_string(name)
        client._send(RequestType.TENSOR_STORE_REMOVE, msg)

        # Handle response
        client._recv()

    ## Constructor for opening an existing store.
    def __init__(self, client: "MDBClient", name: str) -> None:
        ## Client instance.
        self.client = client
        ## Name of the store.
        self.name = name
        ## Fixed size for the tensors.
        self.tensor_size = None

        self._tensor_store_id = None
        self._closed = True
        self._open()

    ## Returns `True` if the store is open.
    def is_closed(self) -> bool:
        return self._closed

    ## Closes the store.
    def close(self) -> None:
        if not self._closed:
            self._close()

    ## Returns the number of tensors in the store.
    def __len__(self) -> int:
        return self.size()

    ## Enter context manager.
    def __enter__(self):
        return self

    ## Exit context manager.
    def __exit__(self, *_):
        self.close()

    ## Get tensors from the store with the pythonic syntax `store[key]`.
    def __getitem__(self, key: Union[int, str, List[int], List[str]]) -> torch.Tensor:
        if not isinstance(key, str) and isinstance(key, Iterable):
            return self.multi_get(key)
        else:
            return self.get(key)

    ## Insert tensors into the store with the pythonic syntax `store[key] = value`.
    def __setitem__(self, key: Union[int, str, List[int], List[str]], value: torch.Tensor) -> None:
        if not isinstance(key, str) and isinstance(key, Iterable):
            self.multi_insert(key, value)
        else:
            self.insert(key, value)

    ## Returns `True` if the store contains the given key with the pythonic syntax `key in store`.
    def __contains__(self, key: Union[int, str]) -> bool:
        return self.contains(key)

    ## Returns `True` if the store contains the given key.
    @decorators.check_closed
    def contains(self, key: Union[int, str]) -> bool:
        packed_key = b""
        if isinstance(key, int):
            packed_key += packer.pack_bool(True)
            packed_key += packer.pack_uint64(key)
        elif isinstance(key, str):
            packed_key += packer.pack_bool(False)
            packed_key += packer.pack_string(key)
        else:
            raise TypeError(f"Key must be int or str, got {type(key)}")

        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packed_key
        self.client._send(RequestType.TENSOR_STORE_CONTAINS, msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_bool(data, 0)

    ## Inserts a tensor into the store.
    @decorators.check_closed
    def insert(self, key: Union[int, str], tensor: torch.Tensor) -> None:
        packed_key = b""
        if isinstance(key, int):
            packed_key += packer.pack_bool(True)
            packed_key += packer.pack_uint64(key)
        elif isinstance(key, str):
            packed_key += packer.pack_bool(False)
            packed_key += packer.pack_string(key)
        else:
            raise TypeError(f"Key must be int or str, got {type(key)}")

        if tensor.dtype != torch.float32:
            raise ValueError(f"Tensor dtype must be torch.float32, got {type(tensor)}")

        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packed_key
        msg += packer.pack_float_vector(tensor.flatten())
        self.client._send(RequestType.TENSOR_STORE_INSERT, msg)

        # Handle response
        self.client._recv()

    ## Inserts multiple tensors into the store.
    @decorators.check_closed
    def multi_insert(self, keys: Union[List[int], List[str]], tensors: torch.Tensor) -> None:
        packed_key = b""
        if all(isinstance(key, int) for key in keys):
            packed_key += packer.pack_bool(True)
            packed_key += packer.pack_uint64_vector(keys)
        elif all(isinstance(key, str) for key in keys):
            packed_key += packer.pack_bool(False)
            packed_key += packer.pack_string_vector(keys)
        else:
            raise TypeError(f"Key must be List[int] or List[str], got {type(keys)}")

        if tensors.dtype != torch.float32:
            raise ValueError(f"Tensor dtype must be torch.float32, got {type(tensors)}")
        if len(tensors.size()) != 2:
            raise ValueError(f"Tensors must be 2-dimensional, but got {len(tensors.size())}-dimensional tensor")

        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packed_key
        # Written as a plain vector, the server knows the matrix shape
        msg += packer.pack_float_vector(tensors.flatten())
        self.client._send(RequestType.TENSOR_STORE_MULTI_INSERT, msg)

        # Handle response
        self.client._recv()

    ## Gets a tensor from the store.
    @decorators.check_closed
    def get(self, key: Union[int, str]) -> torch.Tensor:
        packed_key = b""
        if isinstance(key, int):
            packed_key += packer.pack_bool(True)
            packed_key += packer.pack_uint64(key)
        elif isinstance(key, str):
            packed_key += packer.pack_bool(False)
            packed_key += packer.pack_string(key)
        else:
            raise TypeError(f"Key must be int or str, got {type(key)}")

        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packed_key
        self.client._send(RequestType.TENSOR_STORE_GET, msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 8
        vector_size = packer.unpack_uint64(data, lo, hi)
        lo, hi = hi, hi + 4 * vector_size
        return torch.tensor(
            data=packer.unpack_float_vector(data, lo, hi),
            dtype=torch.float32,
        )

    ## Gets multiple tensors from the store.
    @decorators.check_closed
    def multi_get(self, keys: Union[List[int], List[str]]) -> torch.Tensor:
        packed_key = b""
        if all(isinstance(key, int) for key in keys):
            packed_key += packer.pack_bool(True)
            packed_key += packer.pack_uint64_vector(keys)
        elif all(isinstance(key, str) for key in keys):
            packed_key += packer.pack_bool(False)
            packed_key += packer.pack_string_vector(keys)
        else:
            raise TypeError(f"Key must be List[int] or List[str], got {type(keys)}")

        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packed_key
        self.client._send(RequestType.TENSOR_STORE_MULTI_GET, msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 8
        vector_size = packer.unpack_uint64(data, lo, hi)
        lo, hi = hi, hi + 4 * vector_size
        return torch.tensor(
            data=packer.unpack_float_vector(data, lo, hi),
            dtype=torch.float32,
        ).reshape(len(keys), self.tensor_size)

    ## Returns the number of tensors in the store.
    @decorators.check_closed
    def size(self) -> int:
        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        self.client._send(RequestType.TENSOR_STORE_SIZE, msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_uint64(data, 0, 8)

    def _open(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_string(self.name)
        self.client._send(RequestType.TENSOR_STORE_OPEN, msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 8
        self._tensor_store_id = packer.unpack_uint64(data, lo, hi)
        lo, hi = hi, hi + 8
        self.tensor_size = packer.unpack_uint64(data, lo, hi)
        self._closed = False

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_uint64(self._tensor_store_id)
        self.client._send(RequestType.TENSOR_STORE_CLOSE, msg)

        # Handle response
        self.client._recv()
        self.tensor_size = None
        self._tensor_store_id = None
        self._closed = True
