import numpy as np
import cv2 as cv
import os
import json
import shutil



class MemoryManager:
    def __init__(self, dir_path : str, temp_dir : str):
        self.dir_path = dir_path
        self.temp_dir = temp_dir

        #Check if the directory exists
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        #Init researcher data
        self.load_researchers()

        #Clear the temp directory
        self.clean_temp_dir()
    
    @property
    def researchers(self):
        return self._researchers

    def load_researchers(self):
        try:
            with open(os.path.join(self.dir_path,"researchers.json"), "r") as file:
                self._researchers = json.load(file)
        except FileNotFoundError:
            self._researchers = []

    def push_researcher(self, researcher_id):
        if researcher_id in self._researchers:
            return
        self._researchers.append(researcher_id)

        with open(os.path.join(self.dir_path, "researchers.json"), "w") as file:
            file.write(json.dumps(self._researchers))

    def clean_temp_dir(self):
        '''
            Clean recursively the temp directory
        '''

        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)

    def save_img(self, session_id : str, img : np.ndarray, name : str) -> str:
        '''
            Save an image in the session directory and return the path
        '''
        path = os.path.join(self.temp_dir, str(session_id))
        if not os.path.exists(path):
            os.makedirs(path)

        full_path = os.path.join(path, name)
        cv.imwrite(full_path, img)

        return f"{session_id}/{name}"
    
    

    def release_session(self, session_id : str):
        '''
            Remove a session directory
        '''
        path = os.path.join(self.temp_dir, str(session_id))
        if os.path.exists(path):
            for filename in os.listdir(path):
                os.remove(os.path.join(path, filename))
            os.rmdir(path)
        else:
            print("Session not found")
            
 








        
