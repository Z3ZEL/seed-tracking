import argparse

PARSER = argparse.ArgumentParser(description='SeedTracker')
PARSER.add_argument('-i', '--input', type=str, required=False, default='data', help='Input folder containing the images')



def parse_args():
    return PARSER.parse_args()

def get_input_folder():
    return parse_args().input