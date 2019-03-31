import pandas as pd

def tag_messages(log_data, sources):
    """
    Wrapper to keep all of the tagging we will do, just so that we don't clutter the main function
    """
    # Mark the source
    source_string = '(' + '|'.join(sources) + ')'
    log_data['source'] = log_data.message.str.extract(source_string, expand = False).fillna('missing')

    # Mark if it was scraping of a URL
    log_data['is_scrape'] = log_data.message.str.contains('Scraping URL')

    # Mark if it is the finding of a duplicate
    log_data['is_duplicate'] = log_data.message.str.contains('duplicate link')

    # Mark if was an error
    log_data['is_error'] = log_data.message.str.contains('found an error')

    # Mark if a pulling problem
    log_data['is_pull_fail'] = log_data.message.str.contains('not managed to pull')

    # Not valid
    log_data['is_not_valid'] = log_data.message.str.contains('link found is not valid')

    # Is fake link
    log_data['is_fake_link'] = log_data.message.str.contains('fake_link')

    # Is only suburl
    log_data['is_only_suburl'] = log_data.message.str.contains('Returning the original URL')

    # How many headlines looked at
    log_data['is_headlines'] = log_data.message.str.contains('looking at the headlines')

def summarise_log(log_loc, log_name = 'full_process_logfile.log'):
    """
    Wrapper that will load in the log from the current run and then do a summary on it
    Will save the result in the log folder
    This script should run after the cleanup - so it will summarise the cleanup of yesterday's content
    """
    sources = ['bbc', 'dailymail', 'theguardian', 'skysports', 'telegraph']

    # Load in the data
    log_data = pd.read_csv(log_loc / log_name, sep = '    ', names = ['timestamp', 'type', 'process', 'message'])