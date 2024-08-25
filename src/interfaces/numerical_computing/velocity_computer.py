from interfaces.numerical_computing.numerical_computer import NumericalComputer

class VelocityComputer(NumericalComputer):
    """
        Don't use this class directly, use the child classes instead. 
        If you need to implement your own velocity algorithm, inherit from this class and implement the compute method.
        Put the file in the computations file and specify the path of your file in the config file.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def compute(self, m_vector4, s_vector4) -> tuple[float, float]:
        '''
        Computes the velocity of the object.

        Args:
            m_vector4 (np.array): main vector (x,y,z,t).
            s_vector4 (np.array): worker vector (x,y,z,t).


        Returns:
            float: Velocity of the object.
            float: Absolute error of the velocity.

        '''

        raise NotImplementedError("Method compute not implemented")
