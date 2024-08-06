from interfaces.numerical_computing.numerical_computer import NumericalComputer

class DataCleaner(NumericalComputer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def compute(self, m_pos_ts, s_pos_ts) -> tuple[list, list]:
        '''
        Perform cleaning on the dataset of seed positions, in image coordinates.

        Args:
            m_pos_ts (list): pos, ts for main image.
            s_pos_ts (list): pos, ts for worker image.


        Returns:
            list: Cleaned main image coordinates.
            list: Cleaned worker image coordinates.

        '''

        raise NotImplementedError("Method compute not implemented")
