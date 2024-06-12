from lib.image_processing import Optimizer, Processor

import numpy as np

class SmoothOptimizer(Optimizer):
    def __init__(self, image_set : list[np.array], iteration : int = 1, **kwargs):
        self.image_set = image_set
        self.iteration = iteration
        self.kernel_size = 5 if 'kernel_size' not in kwargs else kwargs['kernel_size']
    
    def optimize(self, processor : Processor):
        mean_image = np.mean(self.image_set, axis=0)
        mean_image = mean_image.astype(np.uint8)
        for _ in range(self.iteration):
            processor.process(mean_image)       
        processor.process(self.image_set[0])     
