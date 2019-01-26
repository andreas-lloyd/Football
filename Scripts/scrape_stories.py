"""
Main script to execute everything - will set up as a .py to execute from command line
"""

import sys
from pathlib import Path
import datetime
from football_functions.generic import default_logger
from football_functions.processes import process_baseurls as pb

def scrape_stories(HOME_PATH, baseurl_loc, data_name):
    """
    Define a main for execution where we define some stuff
    """

    # Define folder locations
    data_loc = HOME_PATH / data_name
    story_loc = data_loc / 'Stories'
    log_loc = data_loc / 'Logs'

    # For now no proxy
    proxy = None

    # Set up a date for saving - fix so that save in subdirectories
    date_today = datetime.datetime.today().strftime('%Y/%m/%d')

    # And a logger
    process_logger = default_logger.get_logger(log_loc, date_today, 'full_process')

    # And finall execute the full script - COULD ADD A TRY EXCEPT WITH KEYBOARD INTERRUPT AND WRITE TO LOGGER
    pb.full_process(baseurl_loc, proxy, process_logger, story_loc, date_today)

if __name__ == '__main__':
    HOME_PATH = Path(sys.argv[1])
    baseurl_loc = Path(sys.argv[2])
    data_name = Path(sys.argv[3])

    try:
        scrape_stories(HOME_PATH, baseurl_loc, data_name)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as error:
        with open('~/fatal_error.txt', 'w') as error_file:
            error_file.write('Fatal error encountered, printing error string below:\n\n')
            error_file.write(error)

    