from interfaces.numerical_computing.velocity_computer import VelocityComputer
from sklearn.linear_model import RANSACRegressor
import numpy as np
from resource_manager import CONFIG as config

class Computer(VelocityComputer):
    def __init__(self, **kwargs) -> None:
        self._dry_run = kwargs["dry_run"]
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

        
        m_ransac = RANSACRegressor()
        m_ransac.fit(m_X, m_y)

        s_ransac = RANSACRegressor()
        s_ransac.fit(s_X, s_y)

        if self.plot:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime, timedelta
            
            # Assuming m_X and s_X are numpy arrays of UNIX timestamps
            m_X_dates = [datetime.utcfromtimestamp(ts/1e9) for ts in m_X.flatten()]
            s_X_dates = [datetime.utcfromtimestamp(ts/1e9) for ts in s_X.flatten()]
            
            fig, ax = plt.subplots()
            
            # Plotting outliers for m_X and s_X
            outliers_m = np.logical_not(m_ransac.inlier_mask_)
            outliers_s = np.logical_not(s_ransac.inlier_mask_)
        
            # Plotting inliers and RANSAC regressor for m_X
            ax.scatter(m_X_dates, m_y, color='violet', marker='.', label='Inliers (m)')
            m_X_dates_sorted, m_y_ransac_sorted = zip(*sorted(zip(m_X_dates, m_ransac.predict(m_X))))
            ax.plot(m_X_dates_sorted, m_y_ransac_sorted, color='purple', linewidth=2, label='RANSAC regressor (m)')
            
            # Plotting inliers and RANSAC regressor for s_X
            ax.scatter(s_X_dates, s_y, color='lightblue', marker='.', label='Inliers (s)')
            s_X_dates_sorted, s_y_ransac_sorted = zip(*sorted(zip(s_X_dates, s_ransac.predict(s_X))))
            ax.plot(s_X_dates_sorted, s_y_ransac_sorted, color='cornflowerblue', linewidth=2, label='RANSAC regressor (s)')


            ax.scatter([m_X_dates[i] for i in range(len(m_X)) if outliers_m[i]], [m_y[i] for i in range(len(m_X)) if outliers_m[i]], color='darkmagenta', marker='.', label='Outliers (m)')
            ax.scatter([s_X_dates[i] for i in range(len(s_X)) if outliers_s[i]], [s_y[i] for i in range(len(s_X)) if outliers_s[i]], color='darkblue', marker='.', label='Outliers (s)')
            
            # Formatting the date on the x-axis
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            fig.autofmt_xdate()
            
            ax.set_xlabel('Time')
            ax.set_ylabel('Y')
            ax.legend(loc='lower right')


            if not self._dry_run:
                import os
                plt.savefig(os.path.join(config["master_camera"]["temp_directory"], f"plot_{id}_velocity.png"))


        m_velocity = m_ransac.estimator_.coef_
        s_velocity = s_ransac.estimator_.coef_

        mean = float(np.mean([m_velocity, s_velocity], axis=0) * 1e7)
        return mean , float(max(m_velocity * 1e7, s_velocity * 1e7) - mean)
       








