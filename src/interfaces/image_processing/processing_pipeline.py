import numpy as np
import cv2
class ProcessingLayer:
    def __init__(self, **kwargs):
        self.show = False if 'show' not in kwargs else kwargs['show']
        self.duration = 500 if 'duration' not in kwargs else kwargs['duration']
    def transform(self, image : np.array) -> np.ndarray:
        pass
    def apply(self, image : np.array) -> np.ndarray:
        image = self.transform(image)

        if self.show:
            cv2.imshow('image', image)
            cv2.waitKey(self.duration)
            cv2.destroyAllWindows()

        return image

