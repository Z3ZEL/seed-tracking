from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server_lib.device import Device
import io,sys
from threading import Thread
from server_lib.device_exception import DeviceException
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
        self._log_activated = (not config["dev"] or (config["dev"] and not 'log' in config['dev']))
        self._stdout = io.StringIO() if self._log_activated  else sys.stdout

    def logger(func):
        def wrapper(self : LoggerThread, *args, **kwargs):
            try:
                sys.stdout = self._stdout
                func(self, *args, **kwargs)
                sys.stdout = self._original_stdout
                if self._log_activated:
                    self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue())
            except DeviceException as e:
                sys.stdout = self._original_stdout
                if self._log_activated:
                    self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue(), exception=e)
                self._device.raise_error(e)
            except RuntimeError as e:
                sys.stdout = self._original_stdout
                print("Aborting ...")
                if self._log_activated:
                    self._memory_manager.log_record_output(self._session_id, self._stdout.getvalue() + str("\nAborting ...\n"))
        return wrapper
    






    