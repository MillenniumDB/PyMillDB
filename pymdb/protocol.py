from enum import Enum


class RequestType(Enum):
    # GRAPH EXPLORATION

    # FEATURE STORE
    FEATURE_STORE_CREATE = b"\x10"

    # BATCH LOADER
    BATCH_LOADER_NEW = b"\x01"
    BATCH_LOADER_NEXT = b"\x02"
    BATCH_LOADER_CLOSE = b"\x03"


class StatusCode(Enum):
    SUCCESS = b"\x00"
    UNEXPECTED_ERROR = b"\x01"
