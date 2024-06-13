from interfaces.image_processing import ProcessingLayer
import numpy as np
import cv2

class ThresholdLayer(ProcessingLayer):
    def __init__(self, threshold : int, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def transform(self, image : np.array) -> np.ndarray:
        _, binary = cv2.threshold(image, self.threshold, 255, cv2.THRESH_BINARY)
        return binary