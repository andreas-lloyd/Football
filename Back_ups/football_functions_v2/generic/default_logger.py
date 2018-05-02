'''
Just a set up function for the logger we will be using in general throughout the processes
'''
import logging, os

def get_logger(data_loc, date_today, process, level = logging.INFO):
    '''
    Function that takes today's date and the current process, creates a filename out of it, and then returns a logger that we can use
    '''
    log_loc = os.path.join(data_loc, '99_Logs', date_today)

    # Create a directory for our logs
    if not os.path.exists(log_loc):
        os.makedirs(log_loc)

    # Declare the filename
    file_name = os.path.join(log_loc, process + '_logfile.log')


    # Set up a our different parameters
    formatter = logging.Formatter('%(asctime)s    %(levelname)s    %(message)s', '%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler(file_name)

    # Then get the actual logger
    logger = logging.getLogger(process)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger