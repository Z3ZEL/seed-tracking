from resource_manager import CONFIG

### CLI ARGS

if not(CONFIG["production"]):
    import argparse

    PARSER = argparse.ArgumentParser(description='SeedTracker | Running without any option will trigger the flask server for production')
    PARSER.add_argument('-i', '--input', type=str, required=False, default='data', help='Input folder containing the images')
    PARSER.add_argument( '--dry-run', action='store_true', required=False, default=False, help='No data saving', dest='dry_run')
    PARSER.add_argument("-p", "--plot", action='store_true', help="Plot reports and save in folder", required=False, default=False)
    PARSER.add_argument("-d", "--display", action='store_true', help="Display plots and result images (if no plot args show only result images)", required=False, default=False)
    PARSER.add_argument("-v", "--verbose", action="store_true", help="Verbose all transformations, pipeline etc...", required=False, default=False)
    PARSER.add_argument( "--shot", type=str, help="Enter in dual shot mode, you need to specify the mode  : single for a one time shot and multiple for a burst capture", required=False, dest='shot')
    PARSER.add_argument("--calibrate", type=str, help="Enter in calibration mode, you need to give two input to --input arg separated by coma of the pictures of the main and the worker camera. Path are given like this ./output/*.jpg for instance. You also need to specify the calibration mode : stereo, single, all", required=False, default=None, dest="calibrate")
    PARSER.add_argument("--check-calibration", action="store_true", help="Launch the calibration check tool, add -p (--plot) option to activate the realtime testing. It will use the config.json calibration settings in order to check the accuracy of the settings", required=False, default=False, dest="check_calibrate")
    PARSER.add_argument("--calculate", action="store_true", help="Launch the seed velocity calculation depending on -i image separated by coma, main and worker. By default, output image are written and no plots are made.", dest="calculate", default=False, required=False)
    PARSER.add_argument("--run", "-r", action="store_true", help="Run a velocity recording, it includes the shooting and the calculation of the seed speed", required=False, default=False)
    PARSER.add_argument("--dev", action="store_true", help="Launch the server in test mode for development only. The device will be a mock one, meaning it won't use the real device, it produces fake data.", required=False, default=False)
    PARSER.add_argument("-c","--clean", action="store_true", help="Clean the output folder", required=False, default=False)
    PARSER.add_argument("-s", "--worker", action="store_true", help="Launch the CLI in worker mode", required=False, default=False)
    def parse_args():
        return PARSER.parse_args()
    def get_args_dict():
        return vars(parse_args())
else:
    def parse_args():
        return None
            
    def get_args_dict():
        ### Production configuration
        return {
            "worker":False,
            "plot":True,
            "verbose":False,
            "dry_run":False,
            "display":False,
            "input":"data",
            "shot":None,
            "calibrate":None,
            "check_calibrate":False,
            "camera_test":False,
            "calculate":False,
            "run":False,
            "dev":False,
            "clean":False
        } | (CONFIG["production_config"] if "production_config" in CONFIG else {} )


def get_input_folder():
    return get_args_dict()["input"]

def get_output_folder():
    return get_args_dict()["output"]

def is_main():
    return not(get_args_dict()["worker"])

## Check output folder
def check_output_folder():
    import os
    output = CONFIG["main_camera"]["temp_directory"] if is_main() else CONFIG["worker_camera"]["temp_directory"]
    path = os.path.join(output)
    os.makedirs(path, exist_ok=True)
        
    
