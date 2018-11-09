"""
Main script to execute everything - will set up as a .py to execute from command line
"""

import sys
from pathlib import Path
import datetime
from football_functions.generic import default_logger
from football_functions.processes import process_baseurls as pb

def main(HOME_PATH):
    """
    Define a main for execution where we define some stuff
    """

    # Define folder locations
    data_loc = HOME_PATH / 'Data'
    organ_loc = data_loc / 'Organisation'
    story_loc = data_loc / 'Stories'
    log_loc = data_loc / 'Logs'

    # Set up a date for saving
    date_today = datetime.datetime.today().strftime('%Y%m%d')

    # And a logger
    process_logger = default_logger.get_logger(log_loc, date_today, 'full_process')

    # And finall execute the full script
    pb.full_process(baseurl_loc, proxy, logger, save_path, date_today)

if __name__ == '__main__':
    

    