"""
Main script to execute everything - will set up as a .py to execute from command line
"""

import sys
from pathlib import Path
import datetime
from football_functions.generic import default_logger
from football_functions.generic import cleanup
from football_functions.processes import process_baseurls as pb

def scrape_stories(HOME_PATH, baseurl_loc, data_name, bucket_name, date_today):
    """
    Define a main for execution where we define some stuff
    """

    # Define folder locations
    data_loc = HOME_PATH / data_name
    story_loc = data_loc / 'Stories'
    log_loc = data_loc / 'Logs'

    # For now no proxy
    proxy = None

    # And a logger
    process_logger = default_logger.get_logger(log_loc, date_today.strftime('%Y/%m/%d'), 'full_process')

    # And finally execute the full script - COULD ADD A TRY EXCEPT WITH KEYBOARD INTERRUPT AND WRITE TO LOGGER
    pb.full_process(baseurl_loc, proxy, process_logger, story_loc, date_today.strftime('%Y/%m/%d'))

    # After finished, start the loop that copys stuff over
    cleanup.move_files(date_today, data_name, bucket_name, process_logger, log_loc, story_loc)

if __name__ == '__main__':
    HOME_PATH = Path(sys.argv[1])
    baseurl_loc = Path(sys.argv[2])
    data_name = sys.argv[3]
    bucket_name = sys.argv[4]

    # Set up a date for saving - fix so that save in subdirectories
    date_today = datetime.datetime.today()

    try:
        scrape_stories(HOME_PATH, baseurl_loc, data_name, bucket_name, date_today)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as error:
        with open('~/fatal_error_{}.txt'.format(date_today.strftime('%Y/%m/%d')), 'w') as error_file:
            error_file.write('Fatal error encountered, printing error below:\n\n')
            error_file.write(error)

        raise

    