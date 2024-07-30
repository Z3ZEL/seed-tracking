import enum
class DeviceError(enum.Enum):
    DEVICE_BUSY = 2
    DEVICE_NO_SESSION = 5
    DEVICE_STATE_NOT_ALLOWED = 3
    NO_RECORD_FOUND = 4
    DEVICE_INTERNAL = -1

    def __str__(self):
        return str(self.name)


class DeviceException(Exception):
    def __init__(self, message):
        super(DeviceException, self).__init__(message)
        self.error_code = 1
class DeviceInternalException(DeviceException):
    def __init__(self, message):
        super(DeviceInternalException, self).__init__(message)
        self.error_code = -1

class DeviceBusyException(DeviceException):
    def __init__(self):
        super(DeviceBusyException, self).__init__("Device is busy, please try again later")
        self.error_code = 2
class DeviceNoSessionException(DeviceException):
    def __init__(self):
        super(DeviceNoSessionException, self).__init__("No session found")
        self.error_code = 5
class DeviceStateNotAllowed(DeviceException):
    def __init__(self):
        super(DeviceStateNotAllowed, self).__init__("Device is not in right state")
        self.error_code = 3
class NoRecordFound(DeviceException):
    def __init__(self):
        super(NoRecordFound, self).__init__("No record found")
        self.error_code = 4

class DeviceRecordException(DeviceException):
    def __init__(self, message):
        super(DeviceRecordException, self).__init__(message)
        self.error_code = 6