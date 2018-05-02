'''
Functions that will follow the process for analysing the baseurls
'''

from football_functions.generic import pull_html

def scrape_urls(baseurl_loc, html_loc, date_today, proxy, logger):
    '''
    Main function that will load in the base URL list and the scrape each one individually and save
    Takes the location of baseurls list in file and the location of 01_HTML in the /Data/ folder
    '''
    # Get an empty list to contain the errors etc.
    error_report = []
    mode = 'base_urls'
    
    logger.info('Loading URLs from {}'.format(baseurl_loc))
    with open(baseurl_loc, 'r') as list_file:
        for url in list_file.readlines():
            error_report.append(pull_html.process_url(url.rstrip(), html_loc, mode, date_today, proxy, logger))
    
    num_urls = len(error_report)
    num_failed = len([(url, error) for url, error in error_report if error != 'No error'])
    logger.info('Finished reading {} URLs, of which {} failed'.format(num_urls, num_failed))
    
    return error_report
    
    
