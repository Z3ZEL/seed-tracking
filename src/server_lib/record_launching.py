from typing import TYPE_CHECKING

from server_lib.record import Record
if TYPE_CHECKING:
    from server_lib.device import Device

import threading
import time
import uuid
import cv2 as cv
import glob
import os

#### Internal import
import actions
from actions.multiple_shot import shot, send_shot
from resource_manager import CONFIG
import args
from server_lib.device_exception import DeviceRecordException
from server_lib.session_record_manager import SessionRecordManager
from server_lib.memory_manager import MemoryManager
from server_lib.logger_thread import LoggerThread
from actions.plot import init_plot, redefine_args

##headless
import matplotlib
matplotlib.use('Agg')

class RecordLauncher(LoggerThread):
    '''
        The linking object between the real device and the backend server
    '''

    def __init__(self, device: 'Device', record_manager: SessionRecordManager, memory_manager : MemoryManager, session_id: str, duration : int, delay : int = 2, seed_id : str = None) -> None:
        super().__init__(session_id, memory_manager, device)
        self._record_manager = record_manager
        self._duration = duration
        self._delay = delay
        self._seed_id = seed_id
        self._kwargs = args.get_args_dict() | {"plot":True}
        redefine_args(self._kwargs)
        init_plot("plot")
        actions.clean(CONFIG)

        


    def _shooting_picture(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.RECORDING)
        start_ts = int(time.time_ns() + (self._delay * 1e9))
        end_ts = int(start_ts + (self._duration * 1e9))


        try:
            send_shot(start_ts, end_ts, CONFIG, suffix=start_ts)
            m_paths, s_paths, roi = shot(CONFIG["main_camera"]["temp_directory"], start_ts, end_ts, suffix=start_ts)
        except SystemExit:
            raise DeviceRecordException("An issue occured during recording please try again")

        if roi[1] - roi[0] < 0.2 * self._duration * 1e9:
            raise DeviceRecordException("The windows captured is too small aborting...")
        
        m_paths = sorted(m_paths)
        s_paths = sorted(s_paths)

        self._m_paths = m_paths
        self._s_paths = s_paths

    def _calculate(self):
        from server_lib.device import DeviceStatus

        self._device.change_status(DeviceStatus.COMPUTING)
        
        try:
            m_computed, s_computed = actions.calculate_real_world_position(self._m_paths, self._s_paths, CONFIG, **self._kwargs)
        except SystemExit:
            raise DeviceRecordException("There was an error during computing the seed world positions")
        try:
            xz_gap = actions.calculate_max_xz_gap(m_computed, s_computed)
        except SystemExit:
            raise DeviceRecordException("There was an error during gap computing")
        try:
            velocity, error = actions.calculate_velocity(m_computed, s_computed, CONFIG,  **self._kwargs)
        except SystemExit:
            raise DeviceRecordException("There was an error during seed velocity computing")
            
        print(f"Estimated velocity : {round(velocity,3)} m/s +- {round(error,3)} m/s")
        

        ## Fetch plot & image records
        print("Saving results ... ")

        result_paths = glob.glob(os.path.join(CONFIG["main_camera"]["temp_directory"], "*_result_*.jpg"))
        plot_paths = glob.glob(os.path.join(CONFIG["main_camera"]["temp_directory"], "plot*.png"))

        plots = [self._memory_manager.save_img(self._session_id, cv.imread(path), f"plot{str(uuid.uuid4())}.png") for path, i in zip(plot_paths, range(len(plot_paths)))]
        results = [self._memory_manager.save_img(self._session_id, cv.imread(path), f"result{str(uuid.uuid4())}.png") for path, i in zip(result_paths, range(len(result_paths)))]

        ##...

        self._record_manager.add_record(self._session_id, Record(velocity, error, plots, results, len(m_computed), len(s_computed), xz_gap,seed_id = self._seed_id))

        self._device.change_status(DeviceStatus.READY)

    @LoggerThread.logger
    def run(self):  
        self._shooting_picture()
        self.check_abort()
        self._calculate()

            

        

        
    
        



