from interfaces.numerical_computing.data_cleaner import DataCleaner
import numpy as np
class Computer(DataCleaner):
    def __init__(self, **kwargs) -> None:
        self.range = kwargs["range"] if "range" in kwargs else 10
        super().__init__(**kwargs)
    
    def compute(self, m_img_coords, s_img_coords) -> tuple[list, list]:
        '''
        This cleaning algorithm computes the median and remove the points that are too far from the median.

        Args:
            m_img_coords (list): pos, ts for master image.
            s_img_coords (list): pos, ts for slave image.   

        Returns:
            list: Cleaned master image coordinates.
            list: Cleaned slave image coordinates.

        '''

        # Compute the median
        m_median = np.median([pos[0] for pos, ts in m_img_coords], axis=0)
        s_median = np.median([pos[0] for pos, ts in s_img_coords], axis=0)

        # Compute the distance from the median
        m_img_coords = [(pos, ts) for pos, ts in m_img_coords if np.linalg.norm(pos[0] - m_median) < self.range]
        s_img_coords = [(pos, ts) for pos, ts in s_img_coords if np.linalg.norm(pos[0] - s_median) < self.range]

        return m_img_coords, s_img_coords
    

        