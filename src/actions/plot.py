import matplotlib.pyplot as plt
from args import get_args_dict as args
from resource_manager import CONFIG as config
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates



kwargs = args()

def redefine_args(_kwargs):
    global kwargs
    kwargs = _kwargs
    

__plot_id = 0

def init_plot(plot_id : str):
    global __plot_id
    __plot_id = plot_id


def plot_wrapper(plot_name : str):
    """
    A decorator to register a function as a plotting function, 
    it automatically saves the plot to a file and create the fig for you.
    Parameters:
        plot_name (str): The name of the plot.

    """
    global __plot_id
    def decorator(func):
        def inner(*args, **ka):
            global kwargs
            if not kwargs["plot"]:
                return
            fig, ax = plt.subplots()
            print("plotting", fig, ax)
            func(*args, fig=fig, ax=ax,**ka)
            if kwargs['plot'] and not kwargs['dry_run']:
                plt.savefig(f"{config['main_camera']['temp_directory']}/{__plot_id}_{plot_name}.png")
    
        return inner
    return decorator


def show_plot():
    if kwargs["display"] and kwargs["plot"]:
        plt.show()
        

def _plot_frame_with_timestamp(frames, timestamps, seed_timestamps, is_main=True):

    plt.scatter(frames,timestamps, color="cornflowerblue" if is_main else "navy", label="Frame")

    seed_frame_timestamps = []

    index = []

    for i in range(len(frames)):
        for ts in seed_timestamps:
            if timestamps[i] == ts:
                index.append(i)



    index = sorted(index)

    plt.axvline(x=index[0], color='r')
    plt.axvline(x=index[-1], color='r')

    plt.scatter(index, seed_timestamps, color="red" if is_main else 'darkred', label="Seed founded")

### ALL REGISTERED PLOTS ###


@plot_wrapper("frame_sync")
def plot_frame_with_timestamp(m_frames, m_timestamps, m_seed_timestamps, s_frames, s_timestamps, s_seed_timestamps, **kwargs):
    """
    Plot frames with timestamps for main and secondary data.

    Args:
        m_frames (list): List of main frames.
        m_timestamps (list): List of main timestamps.
        m_seed_timestamps (list): List of main seed timestamps.
        s_frames (list): List of secondary frames.
        s_timestamps (list): List of secondary timestamps.
        s_seed_timestamps (list): List of secondary seed timestamps.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    _plot_frame_with_timestamp(m_frames, m_timestamps, m_seed_timestamps, is_main=True)
    _plot_frame_with_timestamp(s_frames, s_timestamps, s_seed_timestamps, is_main=False)
    plt.xlabel("Frame number")
    plt.ylabel("Timestamp")
    plt.legend()

@plot_wrapper("seed_position")
def plot_seed_positions(m_computed, s_computed, **kwargs):
    """
    Plot the computed Y positions of seeds over time.
    Args:
        m_computed (list): List of tuples containing computed seed positions for main seeds.
                           Each tuple should have the format (x, y, z, timestamp).
        s_computed (list): List of tuples containing computed seed positions for secondary seeds.
                           Each tuple should have the format (x, y, z, timestamp).
        **kwargs: Additional keyword arguments to be passed to the plot function.
    Returns:
        None
    """
    m_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in m_computed]
    s_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in s_computed]
    
    # Extracting timestamps and y positions
    m_timestamps = [item[0] for item in m_computed_plot]
    m_y_positions = [item[1] for item in m_computed_plot]
    s_timestamps = [item[0] for item in s_computed_plot]
    s_y_positions = [item[1] for item in s_computed_plot]

  
    # Plotting
    plt.plot(m_timestamps, m_y_positions, 'o-', label='Computed Y Position')
    plt.plot(s_timestamps, s_y_positions, 'x-', label='Computed Y Position')

    # Formatting the plot
    plt.xlabel('Timestamp')
    plt.ylabel('Y Position (cm from main origin)')
    plt.title('Computed Y Position Over Time')
    plt.legend()

    # Improve formatting of timestamps on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

@plot_wrapper("seed_position_mean")
def plot_mean_x(m_savePos, s_savePos, m_x_mean, s_x_mean, **kwargs):
    """
    Plot the mean x position of main and worker cameras.
    Parameters:
    - m_savePos (list): List of tuples containing the x and y positions of the main camera.
    - s_savePos (list): List of tuples containing the x and y positions of the worker camera.
    - m_x_mean (float): Mean x position of the main camera.
    - s_x_mean (float): Mean x position of the worker camera.
    - **kwargs: Additional keyword arguments.
    Returns:
    None
    """

    m_pos = np.array([pos for pos, ts in m_savePos])
    s_pos = np.array([pos for pos, ts in s_savePos])
    

    plt.plot(m_pos[:,0], m_pos[:,1], 'ro')
    plt.plot(s_pos[:,0], s_pos[:,1], 'bo')

    #Plot line representing the mean
    plt.axvline(x=m_x_mean, color='r')
    plt.axvline(x=s_x_mean, color='b')

    # Add legend
    plt.legend(["main Camera", "worker Camera", "main Camera Mean", "worker Camera Mean"])
    plt.xlabel(" X Position (px)")
    plt.ylabel(" Y Position (px)")
    
@plot_wrapper("velocity")
def plot_velocity_line(m_X, m_y, s_X, s_y, m_ransac, s_ransac, fig=None, ax=None, **kwargs):            
    """
    Plot the velocity line for two sets of data points along with their RANSAC regressors.
    Parameters:
    - m_X (numpy array): Array of UNIX timestamps for the first set of data points.
    - m_y (numpy array): Array of y-values for the first set of data points.
    - s_X (numpy array): Array of UNIX timestamps for the second set of data points.
    - s_y (numpy array): Array of y-values for the second set of data points.
    - m_ransac (RANSACRegressor): RANSAC regressor for the first set of data points.
    - s_ransac (RANSACRegressor): RANSAC regressor for the second set of data points.
    - fig (matplotlib Figure, optional): Figure object to plot on. If not provided, a new figure will be created.
    - ax (matplotlib Axes, optional): Axes object to plot on. If not provided, a new axes will be created.
    - **kwargs: Additional keyword arguments to pass to the plotting functions.
    Returns:
    - None
    """
    # Assuming m_X and s_X are numpy arrays of UNIX timestamps
    m_X_dates = [datetime.utcfromtimestamp(ts/1e9) for ts in m_X.flatten()]
    s_X_dates = [datetime.utcfromtimestamp(ts/1e9) for ts in s_X.flatten()]
        
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
    # fig.autofmt_xdate()
    
    ax.set_xlabel('Time (ns)')
    ax.set_ylabel('Y (cm, from main origin)')
    ax.legend(loc='lower right')


### END OF REGISTERED PLOTS ###