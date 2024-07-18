import cv2
import args
import resource_manager 
config = resource_manager.CONFIG
import matplotlib.pyplot as plt

def release_imgs(m_paths, s_paths):
    resource_manager.delete_paths(m_paths)
    resource_manager.delete_paths(s_paths)

def get_highest_number(directory):
    import os,re
    highest_number = 0
    pattern = re.compile(r'_([0-9]+)\.jpg$')
    if not os.path.exists(directory):
        return 0

    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            match = pattern.findall(filename)
            if match:
                number = int(match[-1])  # Prendre le dernier groupe de chiffres
                if number > highest_number:
                    highest_number = number

    return highest_number

def plot_seed_positions(m_computed, s_computed):
    import matplotlib.dates as mdates
    import numpy as np
    from datetime import datetime

    m_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in m_computed]
    s_computed_plot = [(datetime.fromtimestamp(ts / 1e9), y) for x,y,z,ts in s_computed]
    
    # Extracting timestamps and y positions
    m_timestamps = [item[0] for item in m_computed_plot]
    m_y_positions = [item[1] for item in m_computed_plot]
    s_timestamps = [item[0] for item in s_computed_plot]
    s_y_positions = [item[1] for item in s_computed_plot]

  
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(m_timestamps, m_y_positions, 'o-', label='Computed Y Position')
    plt.plot(s_timestamps, s_y_positions, 'x-', label='Computed Y Position')

    # Formatting the plot
    plt.xlabel('Timestamp')
    plt.ylabel('Y Position')
    plt.title('Computed Y Position Over Time')
    plt.legend()

    # Improve formatting of timestamps on the x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()


def main():
    kwargs = vars(args.parse_args())
    print(kwargs)
    plot = kwargs["plot"]
    verbose = kwargs["verbose"]
    if verbose:
        kwargs["show"] = True

    if(kwargs['camera_test']):
        from camera import camera_test
        camera_test()
        exit(0)
    if(kwargs['clean']):
        import os
        folder = config["master_camera"]["temp_directory"]
        for filename in os.listdir(folder):
            if filename.endswith('.jpg'):
                os.remove(os.path.join(folder, filename))
        exit(0)
    if(kwargs["shot"] == "single"):
        import time,os, socket
        from actions.single_shot import shot, send_shot, fetch_shot
        print("SHOT TIME !")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        

        #Retrieve the current highest number
        current = get_highest_number(config["master_camera"]["temp_directory"])

        
        current += 1
        while True:
            input("Press enter to shot")
            target_timestamp = int(time.time_ns() + (2 * 10**9)) # 1 second shift


            # Send cmd to slave
            send_shot(sock, target_timestamp, config, suffix=current)
            
            m_path, s_path = shot("output", target_timestamp,suffix=current)


            current += 1
            
            if(kwargs['plot']):
                m_img = cv2.imread(m_path)
                s_img = cv2.imread(s_path)
                cv2.imshow("Master", m_img)
                cv2.imshow("Slave", s_img)
                cv2.waitKey(3000)
                cv2.destroyAllWindows()

            if(kwargs['dry_run']):
                os.remove(s_path)
                os.remove(m_path)



        exit(0)
    if(kwargs["shot"] == "multiple"):
        import time, os, socket
        import numpy as np
        from actions.multiple_shot import shot, fetch_shot, send_shot
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        number = int(time.time())
        
        input("Input press enter to start multiple shot")
        start_timestamp = time.time_ns() + 2*10**9
        end_timestamp = start_timestamp + 2*10**9 # last 2 seconds

        send_shot(sock, start_timestamp, end_timestamp, config, suffix=number)

        m_paths, s_paths, roi = shot(config["master_camera"]["temp_directory"], start_timestamp, end_timestamp, suffix=number)
        m_paths = sorted(m_paths)
        s_paths = sorted(s_paths)
        if(kwargs['plot']):
            m_data = []
            s_data = []

            for i in range(len(m_paths)):
                m_data.append((i,resource_manager.extract_timestamp(m_paths[i].split("/")[-1])))
            for i in range(len(s_paths)):
                s_data.append((i,resource_manager.extract_timestamp(s_paths[i].split("/")[-1])))
            
            import matplotlib.pyplot as plt

            m_data = np.array(m_data)
            s_data = np.array(s_data)

            plt.plot(m_data[:,0], m_data[:,1], color="red")
            plt.axhline(y=roi[0], color='green', linestyle='--', label=f'Min')
            plt.axhline(y=roi[1], color='green', linestyle='--', label=f'Max')
            plt.plot(s_data[:,0], s_data[:,1], color="blue")

            plt.show()
        if(kwargs['dry_run']):
            print("Deleting images")
            for path in m_paths + s_paths:
                os.remove(path)
        exit(0)
    if(kwargs["shot"] == 'stress'):
        from camera import camera_test

        camera_test()
        
    if(kwargs['calibrate']):
        from actions.calibrate import calibrate

        dirs = args.get_input_folder().split(',')
        if len(dirs) != 2:
            print("Error : you must provide two directories to --input separated by comma, the first for the master camera , the second for the slave")
            exit(1)
        
        calibrate(dirs[0], dirs[1], config["calibration"],kwargs["dry_run"], plot, kwargs['calibrate'])
        exit(0)

    if(kwargs['check_calibrate']):
        from actions.calibrating_control import calibrating_control
        calibrating_control(config, kwargs["plot"])
        exit(0)
    
    if kwargs['calculate']:
        from actions.calculate import calculate_real_world_position, calculate_velocity
        import glob
        import numpy as np
       
        m_path, s_path = tuple(args.get_input_folder().split(','))
        m_paths, s_paths = sorted(glob.glob(m_path)), sorted(glob.glob(s_path))

        m_computed, s_computed = calculate_real_world_position(m_paths, s_paths, config, **kwargs)

        if kwargs['plot']:
            plot_seed_positions(m_computed, s_computed)

        velocity, error = calculate_velocity(m_computed, s_computed, config, **kwargs)


        print(f"Estimated velocity : {round(velocity,3)} m/s +- {round(error,3)} m/s")


        # Plotting
        if kwargs['plot']:
            plt.show()
        exit(0)

            
    if kwargs['run']:
        import time, os, socket
        from actions.multiple_shot import shot, fetch_shot, send_shot
        from actions.calculate import calculate_real_world_position, calculate_velocity

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        number = int(input("Enter an ID number"))
        duration = 3
        input("Input press enter to start multiple shot")
        start_timestamp = time.time_ns() + 1*1e9
        s_start_timestamp = int(start_timestamp + 0*1e9)
        end_timestamp = start_timestamp + duration * 10**9 # last 2 seconds
        s_end_timestamp = int(s_start_timestamp + duration * 1e9)

        send_shot(sock, s_start_timestamp, s_end_timestamp, config, suffix=number)

        m_paths, s_paths, roi = shot(config["master_camera"]["temp_directory"], start_timestamp, end_timestamp, suffix=number)
        
        #If the real range captured is inferior of 50% of the requested duration, then exit
        if roi[1] - roi[0] < 0.2 * duration * 1e9: 
            print("The windows captured is too small aborting...")
            release_imgs(m_paths, s_paths)
            exit(1)

        m_paths = sorted(m_paths)
        s_paths = sorted(s_paths)

        try:
            m_computed, s_computed = calculate_real_world_position(m_paths, s_paths, config, **kwargs)
        except SystemExit:
            if kwargs["dry_run"]:
                release_imgs(m_paths, s_paths)
        if kwargs['plot']:
            plot_seed_positions(m_computed, s_computed)


            if len(m_computed) <=1 or len(s_computed) <= 1:
                print("Must be at least 2 seeds for boths")
                if kwargs["dry_run"]:
                    release_imgs(m_paths, s_paths)
                exit(1)

        try:
            velocity, error = calculate_velocity(m_computed, s_computed, config, **kwargs)
        except SystemExit:
            if kwargs["dry_run"]:
                release_imgs(m_paths, s_paths)
        print(f"Estimated velocity : {round(velocity,3)} m/s +- {round(error,3)} m/s")



        
        if(kwargs['dry_run']):
            print("Deleting images")
            for path in m_paths + s_paths:
                os.remove(path)

        if kwargs["plot"]:
            plt.show()
        exit(0)


    