'''
Just a set up function for the logger we will be using in general throughout the processes
'''
import logging, os

def get_logger(log_loc, date_today, process, level = logging.INFO):
    '''
    Function that takes today's date and the current process, creates a filename out of it, and then returns a logger that we can use
    '''
    save_loc = log_loc / date_today

    # Create a directory for our logs
    if not save_loc.exists():
        save_loc.mkdir(parents = True)

    # Declare the filename
    file_name = process + '_logfile.log'


    # Set up a our different parameters
    formatter = logging.Formatter('%(asctime)s    %(levelname)s    %(message)s', '%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(save_loc / file_name)

    # Then get the actual logger
    logger = logging.getLogger(process)
    logger.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger