from lib.image_processing import ProcessingLayer

import numpy as np
import cv2


class MergeShapeLayer(ProcessingLayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def transform(self, image : np.array) -> np.ndarray:
        #dilation
        kernel = np.ones((10,10),np.uint8)
        dilation = cv2.dilate(image,kernel,iterations = 3)
        #erosion
        erosion = cv2.erode(dilation,kernel,iterations = 3)
        return erosion