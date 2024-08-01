from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from server_lib.device import Device
from server_lib.record import Record
from server_lib.device_exception import DeviceRecordException
from server_lib.session_record_manager import SessionRecordManager
from server_lib.memory_manager import MemoryManager
from server_lib.logger_thread import LoggerThread
from resource_manager import CONFIG 
import args
import uuid
from time import sleep
import random
import cv2 as cv
import numpy as np
import os
def clean(config):
    folder = config["master_camera"]["temp_directory"]
    for filename in os.listdir(folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            os.remove(os.path.join(folder, filename))
class RecordLauncher(LoggerThread):
    '''
        The linking object between the real device and the backend server, the mock one, used to launch the endpoint for development purposes
    '''

    def __init__(self, device: 'Device', record_manager: SessionRecordManager, memory_manager : MemoryManager, session_id: str, duration : int, delay : int = 2, seed_id : str = None) -> None:
        super().__init__(session_id, memory_manager, device)
        self._record_manager = record_manager
        self._duration = duration
        self._delay = delay
        self._seed_id = seed_id
        self._kwargs = args.get_args_dict() | {"plot":True}

        ##clean the temp directory
        clean(CONFIG)


    def _shooting_picture(self):
        from server_lib.device import DeviceStatus
        print("shooting picture")
        self._device.change_status(DeviceStatus.RECORDING)
        sleep(2)
        self._calculate()

    def _calculate(self):
        from server_lib.device import DeviceStatus
        print("calculating")
        

        self._device.change_status(DeviceStatus.COMPUTING)

        master_image_number = random.randrange(0,5)
        slave_image_number = random.randrange(0,5)

        xz_gap = (random.randrange(0,5), random.randrange(0,5))

        if master_image_number == 0 and slave_image_number == 0:
            raise DeviceRecordException("No image found")
            

        seeds = []
        plots = []
        #Create 4 random seed images
        for i in range(4):
            # create a blank image
            img = np.zeros((512,512,3), np.uint8)
            # write seed{i} on the image
            cv.putText(img, f"seed{i}", (10,500), cv.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 2, cv.LINE_AA)
            print("saving seed")
            # save the image
            path = self._memory_manager.save_img(self._session_id,img, f"seed{str(uuid.uuid4())}.jpg")
            # append the seed to the list
            seeds.append(path)
        
        #Create 2 fake plot
        for i in range(2):
            # create a blank image
            img = np.zeros((512,512,3), np.uint8)
            # write plot{i} on the image
            cv.putText(img, f"plot{i}", (10,500), cv.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 2, cv.LINE_AA)
            # save the image
            print("saving plot")
            path = self._memory_manager.save_img(self._session_id,img, f"plot{str(uuid.uuid4())}.jpg")
            # append the plot to the list
            plots.append(path)





        record = Record(random.random() * 3, random.random() * 1, plots, seeds, master_image_number, slave_image_number,xz_gap, seed_id= self._seed_id)
        self._record_manager.add_record(self._session_id, record)
        print("record added")
        sleep(2)
        print("Finished")
        self._device.change_status(DeviceStatus.READY)

    
    @LoggerThread.logger
    def run(self):
        self._shooting_picture()


        
    
        



