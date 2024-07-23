from interfaces.numerical_computing.velocity_computer import VelocityComputer
from sklearn.linear_model import RANSACRegressor
import numpy as np
from actions.plot import plot_velocity_line
from resource_manager import CONFIG as config

class Computer(VelocityComputer):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
    
    def compute(self, m_vector4, s_vector4) -> tuple[float, float]:
        '''
        Computes the velocity of the object.

        Args:
            m_vector4 (np.array): Master vector (x,y,z,t).
            s_vector4 (np.array): Slave vector (x,y,z,t).
        '''

        m_vector4 = np.array(m_vector4)
        s_vector4 = np.array(s_vector4)


        m_X = m_vector4[:, 3].reshape(-1, 1)
        m_y = m_vector4[:, 1].reshape(-1, 1)

        s_X = s_vector4[:, 3].reshape(-1, 1)
        s_y = s_vector4[:, 1].reshape(-1, 1)

        try:
            m_ransac = RANSACRegressor()
            m_ransac.fit(m_X, m_y)

            s_ransac = RANSACRegressor()
            s_ransac.fit(s_X, s_y)
        except ValueError:
            raise SystemExit("Error during RANSAC fitting, not enough data points")
        
        plot_velocity_line(m_X, m_y,s_X,s_y, m_ransac, s_ransac)
            


        m_velocity = m_ransac.estimator_.coef_
        s_velocity = s_ransac.estimator_.coef_

        mean = float(np.mean([m_velocity, s_velocity], axis=0) * 1e7)
        return mean , float(max(m_velocity * 1e7, s_velocity * 1e7) - mean)
       








