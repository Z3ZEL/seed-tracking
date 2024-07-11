from interfaces.image_processing import ProcessingLayer

import numpy as np
import cv2

class ResizeLayer(ProcessingLayer):
    def __init__(self, target_size : tuple, **kwargs):
        super().__init__(**kwargs)
        self.target_size = target_size
    def transform(self, image : np.array) -> np.ndarray:
        return cv2.resize(image, self.target_size)