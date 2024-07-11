from interfaces.image_processing import ProcessingLayer

import numpy as np
import cv2

class UndistortLayer(ProcessingLayer):
    '''Undistort a raw image from a camera given its camera matrix and its distortion coefficient'''
    def __init__(self, mtx, dist, **kwargs):
        super().__init__(**kwargs)
        self.mtx = mtx
        self.dist = dist
    def transform(self, image : np.array) -> np.ndarray:
        return cv2.undistort(image, self.mtx, self.dist, None, None)