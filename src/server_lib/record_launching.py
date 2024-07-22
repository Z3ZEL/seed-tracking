from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server_lib.device import Device
from server_lib.device_exception import DeviceRecordException
from server_lib.session_record_manager import SessionRecordManager, Record
import threading
import time


#### Internal import
import actions
from resource_manager import CONFIG


##headless
import matplotlib
matplotlib.use('Agg')

class RecordLauncher(threading.Thread):
    '''
        The linking object between the real device and the backend server
    '''

    def __init__(self, device: 'Device', record_manager: SessionRecordManager, session_id: str, duration : int, delay : int = 2) -> None:
        super().__init__()
        self._device = device
        self._record_manager = record_manager
        self._session_id = session_id
        self._duration = duration
        self._delay = delay
        actions.clean(CONFIG)

        


    def _shooting_picture(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.RECORDING)
        start_ts = time.time_ns() + self._delay * 1e9
        end_ts = start_ts + self._duration * 1e9
        m_paths, s_paths, roi = actions.shot(CONFIG["master_camera"]["tempdirectory"], start_ts, end_ts, suffix=self._session_id)

        if roi[1] - roi[0] < 0.2 * self._duration * 1e9:
            raise DeviceRecordException("The windows captured is too small aborting...")
        
        m_paths = sorted(m_paths)
        s_paths = sorted(s_paths)

        self._m_paths = m_paths
        self._s_paths = s_paths
        self._calculate()

    def _calculate(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.COMPUTING)
        
        m_computed, s_computed = actions.calculate_real_world_position(self._m_paths, self._s_paths, CONFIG, {"plot": True})

        if len(m_computed) <=1 or len(s_computed) <= 1:
            raise DeviceRecordException("Less than 2 points detected for at least one of the cameras aborting...")
        
        velocity, error = actions.calculate_velocity(m_computed, s_computed, CONFIG, {"plot": True})

        print(f"Estimated velocity : {round(velocity,3)} m/s +- {round(error,3)} m/s")


        ## Fetch plot & image records

        ##...


        self._record_manager.add_record(self._session_id, Record(velocity, error, [], []))


        self._device.change_status(DeviceStatus.READY)

    
    def run(self):
        self._shooting_picture()

        
    
        



