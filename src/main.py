from background_substraction_pipeline import BackgroundSubstractionPipeline
from computations import SeedPosition
import cv2
import args
import image_loader 

def main():
    pipeline = BackgroundSubstractionPipeline(show=True)
    seedPosition = SeedPosition(show=True)
    ims = image_loader.load_images(args.get_input_folder())
    
    for im in ims:
        im = pipeline.process(im)
        print(seedPosition.compute(im))
    
    


if __name__ == '__main__':
    main()
