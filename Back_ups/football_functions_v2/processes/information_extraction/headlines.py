'''
Functions that will extract the headlines from the URLs that we have seen
'''
import pickle, os, re
import football_functions.source_specific.bbc.process_html as bbc # then bbc.process_html.XXX
import football_functions.source_specific.dailymail.process_html as dailymail
import football_functions.source_specific.mirror.process_html as mirror
import football_functions.source_specific.guardian.process_html as guardian
import football_functions.source_specific.skysports.process_html as skysports
import football_functions.source_specific.telegraph.process_html as telegraph

def extract_headlines(html_loc, story_loc, date_today, domain, logger):
    '''
    Function that will extract headlines from the HTML pages previously downloaded (sub and base links)
    Will read the HTML from html_loc and then save to story loc
    What will be saved will come from "source specific" and saved as pickles
    This function works on a single page - takes the domain because sometimes we find 
    odd ones
    '''

    # First the save location
    pickle_path = story_loc + domain + '/' + date_today + '/'

    if not os.path.exists(pickle_path):
        logger.info('Making directory {}'.format(pickle_path))
        os.makedirs(pickle_path)

    # Then load in the HTML content
    logger.debug('Getting content from {}'.format(html_loc))
    with open(html_loc, 'r', encoding = 'utf-8') as html_file:
        html_content = html_file.read()

    # Now do source specific stuff
    if domain == 'bbc':
        modifier = 'football_teams' in html_loc
        articles_info = bbc.extract_headlines(html_content, modifier)

    elif domain == 'dailymail':
        modifier = 'football_index' not in html_loc
        articles_info = dailymail.extract_headlines(html_content, modifier)
        
    elif domain == 'theguardian':
        articles_info = guardian.extract_headlines(html_content)
        
    elif domain == 'mirror':
        articles_info = mirror.extract_headlines(html_content)
    
    elif domain == 'skysports':
        modifier = 'regional' in html_loc
        articles_info = skysports.extract_headlines(html_content, modifier)
        
    elif domain == 'telegraph':
        articles_info = telegraph.extract_headlines(html_content)

    logger.debug('Finished pulling articles - now saving article content')

    # Now have to loop through all of the articles
    for article in articles_info:
        # Name the file in terms of the article that we have pulled
        url_reg = re.search('\/([^\/][^www].*)', articles_info[article]['article_link'])
        
        # Sometimes get weird URLs of other websites
        if url_reg:
            url_extension = url_reg.group(1).replace('/', '_')
        else:
            url_extension = re.sub('[^A-z0-9]', '_', articles_info[article]['article_link'])
        
        pickle_name = re.sub('[^A-z0-9_]+', '', url_extension) + '.pickle'
        
        # Tag on the directory that we made earlier and save to pickle
        pickle_loc = pickle_path + pickle_name
        with open(pickle_loc, 'wb') as article_file:
            pickle.dump(articles_info[article], article_file)

    return articles_info

def process_html(html_loc, story_loc, date_today, logger, domain_list = None):
    '''
    Function for processing the HTML we find and want to process for headlines
    '''

    if domain_list is None:
        domain_list = os.listdir(html_loc)

    # First scan the domains
    for domain in domain_list:
        domain_loc = html_loc + domain + '/' + date_today + '/'

        # Now want to look at all base and sublinks
        link_types = [link_type for link_type in os.listdir(domain_loc) if link_type in ['base_urls', 'sublinks']]
        for link_type in link_types:

            # Then look at the HTML pages we find here
            html_pages = os.listdir(domain_loc + link_type)
            logger.info('Getting headlines from {} HTML pages from {}\n'.format(len(html_pages), domain))
            for html_page in html_pages:
                page_loc = domain_loc + link_type + '/' + html_page
                articles_info = extract_headlines(page_loc, story_loc, date_today, domain, logger)
