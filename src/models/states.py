from enum import Enum


class DeviceState(Enum):
    DETECTED = "detected"
    NOT_DETECTED = "not_detected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class InterfaceState(Enum):
    UP = "up"
    DOWN = "down"
    NOT_FOUND = "not_found"
    ERROR = "error"


class DriverState(Enum):
    DRIVER_PRESENT = "driver_present"
    DRIVER_UNKNOWN = "driver_unknown"
    DRIVER_ERROR = "driver_error"
    DRIVER_NOT_FOUND = "driver_not_found"
    INSUFFICIENT_INFO = "insufficient_info"


class FirmwareState(Enum):
    FIRMWARE_OK = "firmware_ok"
    FIRMWARE_ERROR = "firmware_error"
    FIRMWARE_UNKNOWN = "firmware_unknown"
    LOAD_ERROR = "load_error"
    INSUFFICIENT_INFO = "insufficient_info"


class ConnectionState(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"


class RfkillState(Enum):
    UNBLOCKED = "unblocked"
    BLOCKED = "blocked"
    NOT_FOUND = "not_found"


class NMState(Enum):
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class CommandResultState(Enum):
    SUCCESS = "success"
    COMMAND_NOT_FOUND = "command_not_found"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    NONZERO_EXIT = "nonzero_exit"
    EMPTY_OUTPUT = "empty_output"
    INVALID_OUTPUT = "invalid_output"
    NO_SUCH_DEVICE = "no_such_device"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
