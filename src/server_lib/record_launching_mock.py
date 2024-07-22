from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server_lib.device import Device
from server_lib.device_exception import DeviceRecordException
from server_lib.session_record_manager import SessionRecordManager, Record
import threading
from time import sleep

class RecordLauncher(threading.Thread):
    '''
        The linking object between the real device and the backend server
    '''

    def __init__(self, device: 'Device', record_manager: SessionRecordManager, session_id: str) -> None:
        super().__init__()
        self._device = device
        self._record_manager = record_manager
        self._session_id = session_id


    def _shooting_picture(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.RECORDING)
        sleep(5)
        self._calculate()

    def _calculate(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.COMPUTING)
        record = Record(1, 1,[],[])
        self._record_manager.add_record(self._session_id, record)
        sleep(5)
        self._device.change_status(DeviceStatus.READY)

    
    
    def run(self):
        self._shooting_picture()

        
    
        



