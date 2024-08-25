import numpy as np
class ImageComputer:
    """
    Don't use this class directly, use the child classes instead. 
    If you need to implement your own seed position algorithm for instance,, inherit from this class and implement the compute method.
    Put the file in the computations file and specify the path of your file in the config file."""
     
    def __init__(self, **kwargs):
        self.show = False if 'show' not in kwargs else kwargs['show']
        self.duration = 500 if 'duration' not in kwargs else kwargs['duration']

    def compute(self, image : np.array) -> any:
        pass
    

