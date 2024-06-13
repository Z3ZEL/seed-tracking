import numpy as np
class ImageComputer:
    def __init__(self, **kwargs):
        self.show = False if 'show' not in kwargs else kwargs['show']
        self.duration = 500 if 'duration' not in kwargs else kwargs['duration']

    def compute(self, image : np.array) -> any:
        pass
    

