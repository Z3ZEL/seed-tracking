from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server_lib.device import Device
import io,sys
from threading import Thread
from server_lib.device_exception import DeviceException, DeviceUserAbortException
from server_lib.memory_manager import MemoryManager
from args import get_args_dict
from uuid import UUID   

config = get_args_dict()

class LoggerThread(Thread):
    '''
        Thread to log the output of the record
    '''
    def __init__(self, session_id: UUID, memory_manager: MemoryManager, device: 'Device') -> None:
        super().__init__()
        self._memory_manager = memory_manager
        self._session_id = session_id
        self._device = device

        self._original_stdout = sys.stdout
        self._stdout = io.StringIO() 
        self._abort = False

    def logger(func):
        def wrapper(self : LoggerThread, *args, **kwargs):
            try:
                sys.stdout = self._stdout
                func(self, *args, **kwargs)
                sys.stdout = self._original_stdout
                self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue())
            except DeviceException as e:
                sys.stdout = self._original_stdout
                self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue(), exception=e)
                self._device.raise_error(e)
            except RuntimeError as e:
                sys.stdout = self._original_stdout
                print("Aborting ...")
                self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue() + str("\nAborting ...\n"))
        return wrapper
    

    def abort(self):
        self._abort = True

    def check_abort(self):
        if self._abort:
            raise DeviceUserAbortException()

    