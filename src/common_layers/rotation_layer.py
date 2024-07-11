from interfaces.image_processing import ProcessingLayer

import numpy as np
import cv2

class RotationLayer(ProcessingLayer):
    def __init__(self, rotateCode, **kwargs):
        super().__init__(**kwargs)
        self.rotateCode = rotateCode
    def transform(self, image : np.array) -> np.ndarray:
        return cv2.rotate(image, self.rotateCode)