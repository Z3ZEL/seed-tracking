from numpy import ndarray
from lib.image_processing import Processor
import cv2
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
            ThresholdLayer(threshold=50, **kwargs),
            BlurLayer(kernel_size=5, **kwargs),
            MergeShapeLayer(**kwargs)

        ])

        
    
    def process(self, image: ndarray) -> ndarray:
        return super().process(image)
