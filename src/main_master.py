
import cv2
import args
import resource_manager 
config = resource_manager.CONFIG


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


def main():
    kwargs = vars(args.parse_args())
    print(kwargs)
    plot = kwargs["plot"]

    if(kwargs['camera_test']):
        from camera import camera_test
        camera_test()
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
            target_timestamp = int(time.time_ns() + (1 * 10**9)) # 1 second shift


            # Send cmd to slave
            send_shot(sock, target_timestamp, config, suffix=current)
            
            m_path = shot("output", target_timestamp,suffix=current)

            #Wait a bit
            time.sleep(0.5)

            #Fetch the slave img
            s_path = fetch_shot(config, current)    

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
        from actions.multiple_shot import shot, fetch_shot, send_shot
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        number = int(time.time())
        
        input("Input press enter to start multiple shot")
        start_timestamp = time.time_ns() + 2*10**9
        end_timestamp = start_timestamp + 2*10**9 # last 2 seconds

        send_shot(sock, start_timestamp, end_timestamp, config, suffix=number)

        m_paths = shot(config["master_camera"]["temp_directory"], start_timestamp, end_timestamp, suffix=number)

        time.sleep(0.5)

        s_paths = fetch_shot(config, number)

        print(f"Took {len(m_paths)} pics from the master cam and {len(s_paths)} from the slave cam")
        if(kwargs['plot']):
            #ploting img
            pass
        if(kwargs['dry_run']):
            print("Deleting images")
            for path in m_paths + s_paths:
                os.remove(path)
        exit(0)

    if(kwargs['calibrate']):
        from actions.calibrate import calibrate

        dirs = args.get_input_folder().split(',')
        if len(dirs) != 2:
            print("Error : you must provide two directories to --input separated by comma, the first for the master camera , the second for the slave")
            exit(1)
        
        calibrate(dirs[0], dirs[1], config["calibration"],kwargs["dry_run"], plot)
        exit(0)

    if(kwargs['check_calibrate']):
        from actions.calibrating_control import calibrating_control
        calibrating_control(config, kwargs["plot"])
        exit(0)
    
    if kwargs['calculate']:
        from actions.calculate import calculate_real_world_position
        import glob
        import numpy as np
       
        m_path, s_path = tuple(args.get_input_folder().split(','))
        m_paths, s_paths = sorted(glob.glob(m_path)), sorted(glob.glob(s_path))

        m_computed, s_computed = calculate_real_world_position(m_paths, s_paths, config, **kwargs)

        if kwargs['plot']:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime

            # Example m_computed data structure: [(timestamp1, y1), (timestamp2, y2), ...]
            # Convert timestamps to datetime objects if they're not already
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


        from interfaces.numerical_computing.velocity_computer import VelocityComputer
        from importlib import import_module
        
        velocity_algorithm = import_module("computations."+config['seed_computing']['velocity_algorithm'])
        ransac : VelocityComputer = velocity_algorithm.Computer(**kwargs)

        velocity, error = ransac.compute(m_computed, s_computed)

        print(f"Estimated velocity : {round(velocity,3)} m/s +- {round(error,3)} m/s")


        # Plotting
        if kwargs['plot']:
            plt.show()
        exit(0)

            


if __name__ == '__main__':
    main()

    