import lib.image_processing as ip
import numpy as np
import cv2

class GrayScaleLayer(ip.ProcessingLayer):
    def transform(self, image : np.array) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
