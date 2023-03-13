from typing import TYPE_CHECKING, List

import torch

from ..mdb_client.protocol import RequestType
from ..utils import decorators, packer

if TYPE_CHECKING:
    from ..mdb_client.mdb_client import MDBClient


class TensorStore:
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

    def __init__(self, client: "MDBClient", name: str) -> None:
        self.client = client
        self.name = name

        self.tensor_size = None

        self._tensor_store_id = None
        self._closed = True
        self._open()

    def is_closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        if not self._closed:
            self._close()

    def __len__(self) -> int:
        return self.size()

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def __getitem__(self, key: int | List[int]) -> torch.Tensor:
        if isinstance(key, int):
            return self.get(key)
        else:
            return self.multi_get(key)

    def __setitem__(self, key: int | List[int], value: torch.Tensor) -> None:
        if isinstance(key, int):
            self.insert(key, value)
        else:
            self.multi_insert(key, value)

    def __contains__(self, key: int) -> bool:
        return self.contains(key)

    @decorators.check_closed
    def contains(self, node_id: int) -> bool:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_CONTAINS)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        return packer.unpack_bool(data[0:8])

    @decorators.check_closed
    def insert(self, node_id: int, tensor: torch.Tensor) -> None:
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
        msg += packer.pack_uint64(node_id)
        msg += packer.pack_float_vector(tensor.flatten())
        self.client._send(msg)

        # Handle response
        self.client._recv()

    @decorators.check_closed
    def multi_insert(self, node_ids: List[int], tensors: torch.Tensor) -> None:
        if tensors.dtype != torch.float32:
            raise ValueError(f"Tensor dtype must be torch.float32, got {tensors.dtype}")
        if tensors.shape.numel() != 2:
            raise ValueError(
                f"tensors must be 2-dimensional, but got {tensors.shape.numel()}-dimensional tensor"
            )
        if len(node_ids) != tensors.shape[0]:
            raise ValueError(
                f"The number of node_ids ({len(node_ids)}) does not match the tensors rows ({tensors.shape[0]})"
            )
        if tensors.shape[1] != self.tensor_size:
            raise ValueError(
                f"tensors columns ({tensors.shape[1]}) does not match tensor_size of the store ({self.tensor_size})"
            )

        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_MULTI_INSERT)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(len(node_ids))
        msg += packer.pack_uint64_vector(node_ids)
        msg += packer.pack_float_vector(tensors.flatten())
        self.client._send(msg)

        # Handle response
        self.client._recv()

    @decorators.check_closed
    def get(self, node_id: int) -> torch.Tensor:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_GET)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(node_id)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.tensor_size
        return torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]), dtype=torch.float32
        )

    @decorators.check_closed
    def multi_get(self, node_ids: List[int]) -> torch.Tensor:
        # Send request
        msg = b""
        msg += packer.pack_byte(RequestType.TENSOR_STORE_MULTI_GET)
        msg += packer.pack_uint64(self._tensor_store_id)
        msg += packer.pack_uint64(len(node_ids))
        msg += packer.pack_uint64_vector(node_ids)
        self.client._send(msg)

        # Handle response
        data, _ = self.client._recv()
        lo, hi = 0, 4 * self.tensor_size * len(node_ids)
        return torch.tensor(
            data=packer.unpack_float_vector(data[lo:hi]),
            dtype=torch.float32,
        ).reshape(len(node_ids), self.tensor_size)

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

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}, tensor_size={self.tensor_size})'
