'''
Generic functions for pulling HTML content - should be robust and handle errors, taking any URL as input
'''
import requests, re, os, time, random

def request_html(url, proxy, logger):
    """
    Function that is fed a URL and then tries to pull from it, doing some error checking and handling proxies + sleeping
    """
    
    # Pull the HTML data from the URL using requests
    try:
        response = requests.get(url, proxies = proxy)
        
        # If we 404 then we have connected well
        if response.status_code == 404:
            logger.error('404 Error')
            return (url, '404 error')
        else:
            html_text = response.text
            logger.debug('Successfully pulled HTML from {}'.format(url))
            return (html_text, 'No error')
    except requests.exceptions.RequestException as error:
        # The link timed out
        logger.warning('Have not managed to pull from {} due to a {}'.format(url, error))
        logger.debug('Sleeping for 5 seconds to see if works again')
        time.sleep(5)
        
        # Try again after sleeping for 5 seconds in case we were rejected
        try:
            response = requests.get(url, proxies = proxy)
            
            if response.status_code == 404:
                logger.error('404 Error')
                return (url, '404 error')
            else:
                html_text = response.text
                logger.debug('Successfully pulled HTML from {}'.format(url))
                return (html_text, 'No error')
        except requests.exceptions.RequestException as error:
            logger.error('Still not working')
            return (url, error)

def process_url(url, proxy, logger):
    """
    A function that is given a URL and then checks it over to see if worth scraping
    If valid, will proceed to scrape - so all scraping goes here
    Note that if we produce an error, will return the URL again
    """
    logger.info('Scraping URL {}'.format(url))
    
    # First check if the think we are scraping is valid and remove any spaces
    valid_url = re.match('^http\S*www\.\S*$', url)
    
    if valid_url and 'fake_link' not in url:
        # Always sleep a bit before requesting, just to stop us being rejected so much
        time.sleep(random.uniform(1, 2))
        
        return request_html(valid_url.group(0).rstrip(), proxy, logger)
    elif 'fake_link' in url:
        logger.warning('The link found is fake\n {}\n'.format(url))
        return (url, 'Fake link')
    else:
        logger.warning('The link found is not valid\n {}\n'.format(url))
        return (url, 'Invalid URL')