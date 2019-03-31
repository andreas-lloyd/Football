import subprocess
from pathlib import Path
from datetime import timedelta

def copy_files(loc, data_name, bucket_name, date_yesterday, logger):
    """
    Small wrapper to just abstract some repetitive processes
    Not sure if should add in a part to zip up the jsons - maybe not really necessary

    CHANGE NEEDED - i guess need to loop over sources
    """
    # First build up the locations
    local_path = Path(loc) / date_yesterday.strftime('%Y/%m/%d')
    bucket_path = Path(loc.replace(data_name, bucket_name)) / date_yesterday.strftime('%Y/%m/%d')
    
    # Check that the file we are working with exists, and copy over whole directory
    logger.info('CLEANUP    Looking in {}'.format(local_path))
    if local_path.exists():
        logger.info('CLEANUP   Exists! Copying...')
        command = 'mkdir -p {} && cp -r {}/. {}'.format(bucket_path, local_path, bucket_path)
        subprocess.run(command, shell = True)
    else:
        logger.error('CLEANUP   Path not found')

def move_files(date_today, data_name, bucket_name, logger, log_loc = None, story_loc = None, zip_stories = False):
    """
    A wrapper to move (COPY) some files from local data branch to google cloud branch
    Doing it like this because saving directly is just too slow
    The first thing to move are logs, which do not take up a lot of space
    Secondly will think about zipping and moving stories too
    Note that will save stuff from yesterday (if exists)
    """
    date_yesterday = date_today - timedelta(days = 1)

    if log_loc:
        copy_files(log_loc, data_name, bucket_name, date_yesterday, logger)

    if story_loc:
        for domain_loc in story_loc.iterdir():
            copy_files(domain_loc, data_name, bucket_name, date_yesterday, logger)