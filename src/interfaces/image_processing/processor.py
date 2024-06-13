import interfaces.image_processing.processing_pipeline as pp
import numpy as np
class Processor:
    def __init__(self, layers : list[pp.ProcessingLayer]):
        self.layers = layers

    def process(self, image: np.ndarray) -> np.ndarray:
        tmp = image.copy()
        for layer in self.layers:
            tmp = layer.apply(tmp)

        return tmp