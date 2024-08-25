from numpy import ndarray
from interfaces.image_processing import Processor
import cv2
### This is the main pipeline of the app BackgroundSubstractionPipeline, you can create
### your own pipeline by creating a new class that inherits from Processor and import layer (or create new one)
### it's not an algorithm, so it's not dynamicly imported from the config, you need to manually change it
### in the actions.calculate.py file.


### Importing layer
from background_substraction_pipeline.layers.grayscale_layer import GrayScaleLayer
from background_substraction_pipeline.layers.backgroundremoval_layer import BackgroundRemovalLayer
from background_substraction_pipeline.layers.contrast_layer import ContrastLayer
from background_substraction_pipeline.layers.threshold_layer import ThresholdLayer
from background_substraction_pipeline.layers.blur_layer import  BlurLayer
from background_substraction_pipeline.layers.mergeshape_layer import MergeShapeLayer
####



class BackgroundSubstractionPipeline(Processor):
    def __init__(self, **kwargs):
        '''
        Constructor for the BackgroundSubstractionPipeline, you can add more layers, add parameters to the constructor if needed
        '''
        
        ##Initializing the processor
        self.backgroundSubstractor = cv2.createBackgroundSubtractorMOG2(varThreshold=32)


        ##Building our processing pipeline
        super().__init__([
            
            GrayScaleLayer(**kwargs),
            BackgroundRemovalLayer(self.backgroundSubstractor, **kwargs),
            ContrastLayer(alpha=2, **kwargs),
            BlurLayer(kernel_size=5, **kwargs),
            ThresholdLayer(threshold=180, **kwargs),
            MergeShapeLayer(**kwargs)

        ])

        
    
    def process(self, image: ndarray) -> ndarray:
        return super().process(image)
