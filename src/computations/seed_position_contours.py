from interfaces.image_computing import ImageComputer
import numpy as np
import cv2
class Computer(ImageComputer):
    def __init__(self, **kwargs) -> None:
        self.last_contour = None
        self.history = {}
        super().__init__(**kwargs)
    '''Computes the seed position of the image. Image needs to be passed into a processor.'''
    def compute(self, image : np.array) -> tuple:
        '''
        Computes the seed position of the image. Image needs to be passed into a processor.

        Args:
            image (np.array): Image to compute the seed position.

        Returns:
            tuple: Seed position.
            None: If no seed position is found.
        '''
        image = image.copy()
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # Remove contour
        contours = [contour for contour in contours if cv2.contourArea(contour) > 100]
        if len(contours) == 0:
            return None
        current_contour = max(contours, key=cv2.contourArea)

        if self.last_contour is None:
            self.last_contour = current_contour
        else:
            # Find the most similar contour
            for contour in contours:
                if cv2.matchShapes(self.last_contour, contour, 1, 0.0) < 0.1:
                    current_contour = contour
                    self.last_contour = current_contour
                    break
            if current_contour is None:
                current_contour = max(contours, key=cv2.contourArea)

        # Convert to BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        # Draw contour
        cv2.drawContours(image, [current_contour], -1, (0, 255, 0), 2)


        # find center of mass
        M = cv2.moments(current_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(image, (cX, cY), 5, (255, 0, 255), -1)
            if self.show:
                cv2.imshow('image', image)
                cv2.waitKey(self.duration)
                cv2.destroyAllWindows()
            self.history[(cX, cY)] = self.last_contour
            return cX, cY
        else:
            return None
            