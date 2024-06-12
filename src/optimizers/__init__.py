from optimizers.smooth_optimizer import SmoothOptimizer as SmoothOptimizer
from lib.image_processing.optimizer import Optimizer, Processor


class OptimizerApplier:
    def __init__(self, optimizers : list[Optimizer]):
        self.optimizers = optimizers
    def apply(self, processor : Processor):
        for optimizer in self.optimizers:
            optimizer.optimize(processor)
        