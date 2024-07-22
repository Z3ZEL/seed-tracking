import numpy as np
import cv2 as cv
import os
class MemoryManager:
    def __init__(self, dir_path : str, temp_dir : str):
        self.dir_path = dir_path
        self.temp_dir = temp_dir

        #Check if the directory exists
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        #Clear the temp directory

    def clean_temp_dir(self):
        '''
            Clean recursively the temp directory
        '''

        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))

    def save_img(self, session_id : str, img : np.ndarray, name : str) -> str:
        '''
            Save an image in the session directory and return the path
        '''
        path = os.path.join(self.temp_dir, session_id)
        if not os.path.exists(path):
            os.makedirs(path)

        full_path = os.path.join(path, name)
        cv.imwrite(full_path, img)

        return full_path
    
    def release_session(self, session_id : str):
        '''
            Remove a session directory
        '''
        path = os.path.join(self.temp_dir, session_id)
        if os.path.exists(path):
            for filename in os.listdir(path):
                os.remove(os.path.join(path, filename))
            os.rmdir(path)
        else:
            print("Session not found")
            
 








        
