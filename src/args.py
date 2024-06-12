import argparse

PARSER = argparse.ArgumentParser(description='SeedTracker')
PARSER.add_argument('-i', '--input', type=str, required=False, default='data', help='Input folder containing the images')
PARSER.add_argument('-d', '--display', action='store_true', required=False, default=False, help='Display the images', dest='show')
PARSER.add_argument('-o', '--output', type=str, required=False, default='output', help='Output folder to save the images')
PARSER.add_argument("-p", "--plot", action='store_true', help="Plot the images", required=False, default=False)

def parse_args():
    return PARSER.parse_args()

def get_input_folder():
    return parse_args().input

def get_output_folder():
    return parse_args().output