from typing import TYPE_CHECKING, List

from ..mdb_client.protocol import RequestType
from ..utils import packer

if TYPE_CHECKING:
    from ..mdb_client.mdb_client import MDBClient


class Sampler:
    def __init__(self, client: "MDBClient"):
        self.client = client

    def get_seed_ids(self) -> List[int]:
        msg = b""
        pass
