from background_substraction_pipeline import BackgroundSubstractionPipeline
from computations import SeedPosition
from optimizers import SmoothOptimizer, OptimizerApplier
import cv2
import args
import resource_manager 

def main():
    kwargs = vars(args.parse_args())
    print(kwargs)
    pipeline = BackgroundSubstractionPipeline(**kwargs)
    seedPosition = SeedPosition(**kwargs)
    ims = resource_manager.load_images(args.get_input_folder())
    #Apply the optimizers
    OptimizerApplier([
        SmoothOptimizer(image_set = ims, iteration=4, kernel_size=5)
    ]).apply(pipeline)


    print("Processing images...")
    saveIms = []
    savePos = []
    for im in ims:
        out = pipeline.process(im)
        pos = seedPosition.compute(out)

        if pos is not None:
            ## Concat out and im 
            savePos.append(pos)
            out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
            cv2.circle(out, pos, 5, (0, 0, 255), -1)
            out = cv2.hconcat([im, out])
            saveIms.append(out)
    

    resource_manager.save_images(args.get_output_folder(), saveIms)

    if kwargs["plot"]:
        import matplotlib.pyplot as plt
        #Plot position
        x, y = zip(*savePos)
        #Define x and y max to be im shape
        x_max = ims[0].shape[1]
        y_max = ims[0].shape[0]
        plt.xlim(0, x_max)
        plt.ylim(0, y_max)

        plt.plot(x, y, 'ro')
        plt.show()


        
    
    


if __name__ == '__main__':
    main()
