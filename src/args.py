import argparse

PARSER = argparse.ArgumentParser(description='SeedTracker')
PARSER.add_argument('-i', '--input', type=str, required=False, default='data', help='Input folder containing the images')
PARSER.add_argument( '--dry-run', action='store_true', required=False, default=False, help='No data saving', dest='dry_run')
PARSER.add_argument('-o', '--output', type=str, required=False, default='output', help='Output folder to save the images')
PARSER.add_argument("-p", "--plot", action='store_true', help="Show whatever the process has to show", required=False, default=False)
PARSER.add_argument( "--shot", type=str, help="Enter in dual shot mode", required=False, dest='shot')
PARSER.add_argument("--calibrate", action='store_true', help="Enter in calibration mode, you need to give two input to --input arg separated by coma of the pictures of the master and the slave camera", required=False, default=False, dest="calibrate")
PARSER.add_argument("--check-calibration", action="store_true", help="Launch the calibration check tool, add -p (--plot) option to activate the realtime testing", required=False, default=False, dest="check_calibrate")
PARSER.add_argument("--camera-test", action="store_true", help="Launch a camera test given its configuration to check its performance", dest="camera_test", default=False, required=False)
PARSER.add_argument("--calculate", action="store_true", help="Launch the seed velocity calculation depending on -i image separated by coma, master and slave. -o for output result", dest="calculate", default=False, required=False)
def parse_args():
    return PARSER.parse_args()

def get_input_folder():
    return parse_args().input

def get_output_folder():
    return parse_args().output