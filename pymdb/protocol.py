from enum import IntEnum

DEFAULT_PORT = 8080
BUFFER_SIZE = 4096

END_MASK = 0b1000_0000  # 1000'0000 Set to 1 if it is the last message
ERROR_MASK = 0b0100_0000  # 0100'0000 Set to 1 if the status code is an error
STATUS_MASK = 0b0111_1111  # 0111'1111 Status code


class RequestType(IntEnum):
    # GRAPH EXPLORATION

    # FEATURE STORE

    # BATCH LOADER
    BATCH_LOADER_NEW = 0b0000_0001
    BATCH_LOADER_BEGIN = 0b0000_0010
    BATCH_LOADER_NEXT = 0b0000_0011
    BATCH_LOADER_CLOSE = 0b0000_0100


class StatusCode(IntEnum):
    # SUCCESS CODES
    # Generic success
    SUCCESS = 0b0000_0000
    # An iterator has no more elements
    END_OF_ITERATION = 0b0000_0001

    # ERROR CODES
    # Generic exception
    EXCEPTION = 0b0100_0000
    # An unhandled exception was thrown
    UNEXPECTED_ERROR = 0b0100_0001


def last_message(status: int) -> bool:
    return (status & END_MASK) != 0


def error_status(status: int) -> bool:
    return (status & ERROR_MASK) != 0


def decode_status(status: int) -> "StatusCode":
    return StatusCode(status & STATUS_MASK)
