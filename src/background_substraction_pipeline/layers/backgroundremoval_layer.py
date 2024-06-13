from interfaces.image_processing import ProcessingLayer

import numpy as np
import cv2

class BackgroundRemovalLayer(ProcessingLayer):
    def __init__(self, backgroundSubtractor : cv2.BackgroundSubtractor, **kwargs):
        super().__init__(**kwargs)
        self.backgroundSubtractor = backgroundSubtractor
    def transform(self, image : np.array) -> np.ndarray:
        return self.backgroundSubtractor.apply(image)