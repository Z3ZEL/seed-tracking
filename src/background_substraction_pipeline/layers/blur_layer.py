from interfaces.image_processing import ProcessingLayer

import numpy as np
import cv2


class BlurLayer(ProcessingLayer):
    def __init__(self, kernel_size : int, **kwargs):
        super().__init__(**kwargs)
        self.kernel_size = kernel_size

    def transform(self, image : np.array) -> np.ndarray:
        return cv2.GaussianBlur(image, (self.kernel_size, self.kernel_size), 0)