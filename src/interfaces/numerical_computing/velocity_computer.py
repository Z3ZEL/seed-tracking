from interfaces.numerical_computing.numerical_computer import NumericalComputer

class VelocityComputer(NumericalComputer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def compute(self, m_vector4, s_vector4) -> tuple[float, float]:
        '''
        Computes the velocity of the object.

        Args:
            m_vector4 (np.array): Master vector (x,y,z,t).
            s_vector4 (np.array): Slave vector (x,y,z,t).


        Returns:
            float: Velocity of the object.
            float: Absolute error of the velocity.

        '''

        raise NotImplementedError("Method compute not implemented")
