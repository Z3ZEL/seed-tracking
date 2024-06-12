import lib.image_processing as ip

import numpy as np
import cv2


class ContrastLayer(ip.ProcessingLayer):
    def __init__(self,alpha : float, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha 
    def transform(self, image : np.array) -> np.ndarray:
        return cv2.convertScaleAbs(image, alpha=self.alpha, beta=0)
    