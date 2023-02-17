from enum import IntEnum

DEFAULT_PORT = 8080
BUFFER_SIZE = 4096

END_MASK = 0x80  # 1000'0000 Set to 1 if it is the last message
STATUS_MASK = 0x7F  # 0111'1111 Status code


class RequestType(IntEnum):
    # GRAPH EXPLORATION

    # FEATURE STORE
    FEATURE_STORE_CREATE = 0x10

    # BATCH LOADER
    BATCH_LOADER_NEW = 0x01
    BATCH_LOADER_BEGIN = 0x02
    BATCH_LOADER_NEXT = 0x03
    BATCH_LOADER_CLOSE = 0x04


class StatusCode(IntEnum):
    SUCCESS = 0x00  # Everything went fine
    ERROR = 0x01  # An exception was thrown
    UNEXPECTED_ERROR = 0x02  # An unhandled exception was thrown


def last_message(status: int) -> bool:
    return (status & END_MASK) != 0


def decode_status(status: int) -> "StatusCode":
    return StatusCode(status & STATUS_MASK)
