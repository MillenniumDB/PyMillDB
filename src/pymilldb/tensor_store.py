from typing import TYPE_CHECKING, List, Union

import torch

from .protocol import RequestType
from .utils import decorators, packer

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
        msg += packer.pack_byte(RequestType.TENSOR_STORE_EXISTS)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        client._send(msg)

        # Handle response
        data, _ = client._recv()
        return packer.unpack_bool(data[0:8])

    ## Returns `True` if the store is open.
    @staticmethod
    def is_open(client: "MDBClient", name: str) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_IS_OPEN)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        client._send(msg)

        # Handle response
        data, _ = client._recv()
        return packer.unpack_bool(data[0:8])

    ## Creates a new store on disk.
    @staticmethod
    def create(client: "MDBClient", name: str, tensor_size: int) -> None:
        if tensor_size <= 0:
            raise ValueError(f"tensor_size must be positive integer, got {tensor_size}")
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_CREATE)
        msg += packer.pack_uint64(tensor_size)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        client._send(msg)

        # Handle response
        client._recv()

    ## Removes a store from disk.
    @staticmethod
    def remove(client: "MDBClient", name: str) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_REMOVE)
        msg += packer.pack_uint64(len(name))
        msg += packer.pack_string(name)
        client._send(msg)

        # Handle response
        client._recv()

    ## Returns a list of all store names.
    @staticmethod
    def list(client: "MDBClient") -> List[str]:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_LIST)
        client._send(msg)

        # Handle response
        data, _ = client._recv()
        names = list()
        lo, hi = 0, 8
        num_stores = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8 * num_stores
        name_sizes = packer.unpack_uint64_vector(data[lo:hi])
        for name_size in name_sizes:
            lo, hi = hi, hi + name_size
            names.append(packer.unpack_string(data[lo:hi]))
        return names

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
    def __getitem__(self, key: Union[int, List[int]]) -> torch.Tensor:
        if isinstance(key, int):
            return self.get(key)
        else:
            return self.multi_get(key)

    ## Insert tensors into the store with the pythonic syntax `store[key] = value`.
    def __setitem__(self, key: Union[int, List[int]], value: torch.Tensor) -> None:
        if isinstance(key, int):
            self.insert(key, value)
        else:
            self.multi_insert(key, value)

    ## Returns `True` if the store contains the given key with the pythonic syntax `key in store`.
    def __contains__(self, key: int) -> bool:
        return self.contains(key)

    ## Returns `True` if the store contains the given key.
    @decorators.check_closed
    def contains(self, object_id: int) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_CONTAINS)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(object_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_bool(data[0:8])

    ## Inserts a tensor into the store.
    @decorators.check_closed
    def insert(self, object_id: int, tensor: torch.Tensor) -> None:
        if tensor.dtype != torch.float32:
            raise ValueError(f"Tensor dtype must be torch.float32, got {tensor.dtype}")
        if tensor.numel() != self.tensor_size:
            raise ValueError(
                f"Tensor size ({tensor.numel()}) does not match tensor_size of the store ({self.tensor_size})"
            )

        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_INSERT)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(object_id)
        msg += packer.pack_float_vector(tensor.flatten())
        self.client._send(msg)

        # Handle response
        self.client._recv()

    ## Inserts multiple tensors into the store.
    @decorators.check_closed
    def multi_insert(self, object_ids: List[int], tensors: torch.Tensor) -> None:
        if tensors.dtype != torch.float32:
            raise ValueError(f"Tensor dtype must be torch.float32, got {tensors.dtype}")
        if len(tensors.size()) != 2:
            raise ValueError(
                f"tensors must be 2-dimensional, but got {len(tensors.size())}-dimensional tensor"
            )
        if len(object_ids) != tensors.size(0):
            raise ValueError(
                f"The number of object_ids ({len(object_ids)}) does not match the tensors rows ({tensors.size(0)})"
            )
        if tensors.size(1) != self.tensor_size:
            raise ValueError(
                f"tensors columns ({tensors.size(1)}) does not match tensor_size of the store ({self.tensor_size})"
            )

        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_MULTI_INSERT)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(len(object_ids))
        msg += packer.pack_uint64_vector(object_ids)
        msg += packer.pack_float_vector(tensors.flatten())
        self.client._send(msg)

        # Handle response
        self.client._recv()

    ## Gets a tensor from the store.
    @decorators.check_closed
    def get(self, object_id: int) -> torch.Tensor:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_GET)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(object_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.tensor_size
        return torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
        )

    ## Gets multiple tensors from the store.
    @decorators.check_closed
    def multi_get(self, object_ids: List[int]) -> torch.Tensor:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_MULTI_GET)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(len(object_ids))
        msg += packer.pack_uint64_vector(object_ids)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.tensor_size * len(object_ids)
        return torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]),
            dtype=torch.float32,
        ).reshape(len(object_ids), self.tensor_size)

    ## Returns the number of tensors in the store.
    @decorators.check_closed
    def size(self) -> int:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_SIZE)
        msg += packer.pack_uint64(self._tensor_store_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_uint64(data[0:8])

    def _open(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_OPEN)
        msg += packer.pack_uint64(len(self.name))
        msg += packer.pack_string(self.name)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 8
        self._tensor_store_id = packer.unpack_uint64(data[lo:hi])
        lo, hi = hi, hi + 8
        self.tensor_size = packer.unpack_uint64(data[lo:hi])
        self._closed = False

    def _close(self) -> None:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_CLOSE)
        msg += packer.pack_uint64(self._tensor_store_id)
        self.client._send(msg)

        # Handle response
        self.client._recv()
        self.tensor_size = None
        self._tensor_store_id = None
        self._closed = True
