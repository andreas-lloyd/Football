'''
Generic functions for pulling HTML content - should be robust and handle errors, taking any URL as input
'''
import requests, re, os, time, random

def request_html(url, proxy):
    '''
    Function to request from a URL and do some basic error handling
    '''
    # Pull the HTML data from the URL using requests
    try:
        response = requests.get(url, proxies = proxy)
        
        # If we 404 then we have connected well
        if response.status_code == 404:
            return (url, '404 error')
        else:
            html_text = response.text
            print('Successfully pulled HTML from {}'.format(url))
            return (html_text, 'No error')
    except requests.exceptions.RequestException as error:
        # The link timed out
        print('Have not managed to pull from {} due to a {}'.format(url, error))
        print('Sleeping for 5 seconds to see if works again')
        time.sleep(5)
        
        # Try again after sleeping for 5 seconds in case we were rejected
        try:
            response = requests.get(url, proxies = proxy)
            
            if response.status_code == 404:
                return (url, '404 error')
            else:
                html_text = response.text
                print('Successfully pulled HTML from {}'.format(url))
                return (html_text, 'No error')
        except requests.exceptions.RequestException as error:
            print('Still not working')
            return (url, error)

def get_html(url, html_loc, file_name, mode, domain_name, date_today, proxy):
    '''
    Function to get the URL html and then save it to a directory
    Inputs are the URL to scrape and the location of the "data" section of the file structure (expect .../Data/HTML)
    The file_name is to give a specific name - default is for the base URLs that we search
    The mode is for the file path and which type of link we are processing
    The domain name can be given and it is saved specifically there - or it is not given and searched for in the URL
    '''
    # Pull HTML
    html_text = request_html(url, proxy)

    # If we returned an error want to exit immediately
    if html_text[1] != 'No error':
        return html_text
    
    # Pull the source from the URL for the folder if the domain name is not provided
    if domain_name is None:
        domain_name = re.search('^.*www\.(.*?)\..*', url).group(1) # group looks for matches in ( )s
    
    # Define the file where we are going to save it - each URL should only be pulled once or overwritten
    file_path = html_loc + domain_name + '/' + date_today + '/' + mode + '/'
    html_file =  file_path + file_name + '.html'
    
    print('Saving HTML from URL in \n{}'.format(html_file))
    
    # Check if path exists and if not create it
    if not os.path.exists(file_path):
        print('Making directory {}'.format(file_path))
        os.makedirs(file_path)
    
    # Save the file
    with open(html_file, 'w', encoding = 'utf-8') as f:
        try:
            f.write(html_text[0])
        except:
            print('Unable to write URL to file')
            return (url, 'file error')
    
    print('Successfully saved URL\n')
    
    return (url, 'No error')

def process_url(url, html_loc, mode, date_today, proxy, domain_name = None):
    '''
    A function to process a URL - have decided to work individually as can easily loop on a list
    Takes the URL, location of /Data/, the mode and optionally the domain_name and proxy
    '''
    
    # First check if the think we are scraping is valid and remove any spaces
    valid_url = re.match('^http\S*www\.\S*$', url)
    
    if valid_url and 'fake_link' not in url:
        # Always sleep a bit before requesting, just to stop us being rejected so much
        time.sleep(random.uniform(1, 2))
        
        url_extension = re.search('\/([^\/][^www].*)', valid_url.group(0)).group(1).replace('/', '_')
        file_name = re.sub('[^A-z0-9_]+', '', url_extension)
        return get_html(valid_url.group(0).rstrip(), html_loc, file_name, mode, domain_name, date_today, proxy)
    else:
        print('The link found is not valid\n {}\n'.format(url))
        return (url, 'Invalid URL')