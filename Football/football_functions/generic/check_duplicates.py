import re

def check_duplicates(article_link, domain_path):
    """
    Function for checking for duplicates and stopping us processing the same stories over and over
    Due to the way we are saving - this can only really be done for the headlines, but
    we can do it easily by checking those previous files with similar file names and then loading them in
    if the URL is exactly the same, then we won't pull it
    
    This is important to do BEFORE we move to scrape the HTML, as this is the process that really takes longest
    
    1. Get the file extension
    2. Check for the same extension else where
    3. Since the file name is purely from the URL, we exit saying they are the same
    
    I think this is OK to do, as scraping is really what takes time, and we really do have to scrape the suburl HTML
    """
    # Start building the file name out of the link, checking that everything is valid         
    url_reg = re.search('\/([^\/][^www].*)', article_link)

    # Sometimes get weird URLs of other websites
    if url_reg:
        url_extension = url_reg.group(1).replace('/', '_')
    else:
        url_extension = re.sub('[^A-z0-9]', '_', article_link)

    json_name = re.sub('[^A-z0-9_]+', '', url_extension) + '.json'
    
    # We can use a glob to check for all the files of any pattern under our domain - note that will return False for all fake_links
    if 'fake_link' not in article_link:
        all_matches = list(domain_path.glob('*/*/*/{}'.format(json_name)))
    else:
        all_matches = []

    # If the length is not 0, then we have a duplicate
    return len(all_matches) != 0, json_name