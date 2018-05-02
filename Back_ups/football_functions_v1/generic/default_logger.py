'''
Just a set up function for the logger we will be using in general throughout the processes
'''
import logger, os

def get_logger(data_loc, date_today, process):
    '''
    Function that takes today's date and the current process, creates a filename out of it, and then returns a logger that we can use
    '''
    log_loc = os.path.join(data_loc, '99_Logs')

    # Create a directory for our logs
    if not os.path.exists(log_loc):
        os.makedirs(log_loc)

    # Declare the filename
    file_name = date_today + '_' + process + '_logfile.log'

    logging.basicConfig(
        filename = os.path.join(log_loc, file_name),
        level = logger.DEBUG,
        format = '%(asctime)s    %(levelname)s    %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S')

    return logging.getLogger(process)