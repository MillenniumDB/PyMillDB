from enum import IntEnum

DEFAULT_PORT = 8080
BUFFER_SIZE = 4096

END_MASK = 0b1000_0000  # Set to 1 if it is the last message
ERROR_MASK = 0b0100_0000  # Set to 1 if the status code is an error
STATUS_MASK = 0b0111_1111  # Status code

## Client request type codes.
class RequestType(IntEnum):
    # Sampler
    SAMPLER_SUBGRAPH = 0b0000_0001
    SAMPLER_SUBGRAPH_EDGE_EXISTANCE = 0b0000_0010

    # TENSOR STORE
    # STATIC METHODS
    TENSOR_STORE_EXISTS = 0b0000_0111
    TENSOR_STORE_IS_OPEN = 0b0000_1000
    TENSOR_STORE_CREATE = 0b0000_1001
    TENSOR_STORE_REMOVE = 0b0000_1010
    TENSOR_STORE_LIST = 0b0000_1011
    TENSOR_STORE_OPEN = 0b0000_1100
    # INSTANCE METHODS
    TENSOR_STORE_CLOSE = 0b0000_1101
    TENSOR_STORE_CONTAINS = 0b0000_1110
    TENSOR_STORE_INSERT = 0b0000_1111
    TENSOR_STORE_MULTI_INSERT = 0b0001_0000
    TENSOR_STORE_GET = 0b0001_0001
    TENSOR_STORE_MULTI_GET = 0b0001_0010
    TENSOR_STORE_SIZE = 0b0001_0011


## Server response status codes.
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
