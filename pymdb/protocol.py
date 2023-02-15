from enum import IntEnum


class RequestType(IntEnum):
    # GRAPH EXPLORATION

    # FEATURE STORE

    # BATCH LOADER
    BATCH_LOADER_NEW = 0x01
    BATCH_LOADER_NEXT = 0x02
    BATCH_LOADER_CLOSE = 0x03


class StatusCode(IntEnum):
    SUCCESS = 0x00
    UNEXPECTED_ERROR = 0x01
