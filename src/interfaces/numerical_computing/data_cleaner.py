from interfaces.numerical_computing.numerical_computer import NumericalComputer

class DataCleaner(NumericalComputer):
    """
        Don't use this class directly, use the child classes instead. 
        If you need to implement your own data cleaning algorithm, inherit from this class and implement the compute method.
        Put the file in the computations file and specify the path of your file in the config file.
    """
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
