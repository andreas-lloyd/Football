'''
Functions to scrape the links found in the articles from the earlier script
and then get the text from within
'''
import pickle, os, re
from football_functions.generic import pull_html
from football_functions.source_specific.bbc import process_html as bbc
from football_functions.source_specific.dailymail import process_html as dailymail
from football_functions.source_specific.guardian import process_html as guardian
from football_functions.source_specific.mirror import process_html as mirror
from football_functions.source_specific.skysports import process_html as skysports
from football_functions.source_specific.telegraph import process_html as telegraph

def process_articles(story_loc, html_loc, date_today, proxy, logger, domain_list = None):
    '''
    Function to grab all of the articles saved in pickles and start pulling the HTML found in the URL to get the story
    Note that since this process is so long - will do two loops 
    This is useful for if the internet drops temporarily
    '''
    # Will save the links that do not work for analysis later
    failed_links = []
    mode ='story_link'

    if domain_list is None:
        domain_list = os.listdir(story_loc)

    # Loop over domains and the pickles we find there
    for domain in domain_list:
        pickle_loc = os.path.join(story_loc, domain, date_today)
        for pickle_file in os.listdir(pickle_loc):
            # Load the pickle
            with open(os.path.join(pickle_loc, pickle_file), 'rb') as article_file:
                article_content = pickle.load(article_file)

            # Send the link to be pulled and receive the error type
            error_report = pull_html.process_url(article_content['article_link'], html_loc, mode, date_today, proxy, logger, domain)

            # If we have an error - will append to list to process later
            if error_report[1] != 'No error':
                failed_links.append(error_report)

    logger.info('Finished initial run with {} links that have errors'.format(len(failed_links)))

    # Then process again those that failed
    bad_links = []
    for domain in os.listdir(story_loc):
        for failed_link in failed_links:
            logger.debug('Now looking again at link \n{}'.format(failed_link[0]))

            # Will not look at file errors
            if failed_link[1] != 'File error':
                logger.debug('Not a file error - trying to pull HTML again')

                error_report = pull_html.process_url(failed_link[0], html_loc, mode, date_today, proxy, logger, domain)

                if error_report[1] != 'No error':
                    bad_links.append(error_report)

    logger.info('Finished second run with {} links that are bad'.format(len(bad_links)))

    return bad_links

def get_story(story_path, domain, logger):
    '''
    Function to take the HTML and then get the story text according to the domain
    '''

    logger.debug('Getting the story...')

    if domain == 'bbc':
        story_details = bbc.get_text(story_path, logger)

    elif domain == 'dailymail':
        story_details = dailymail.get_text(story_path, logger)

    elif domain == 'theguardian':
        story_details = guardian.get_text(story_path, logger)

    elif domain == 'mirror':
        story_details = mirror.get_text(story_path, logger)

    elif domain == 'skysports':
        story_details = skysports.get_text(story_path, logger)

    elif domain == 'telegraph':
        story_details = telegraph.get_text(story_path, logger)

    story_dic = {
        'story_text' : re.sub('([a-z0-9])([A-Z])', r'\1.\2', story_details[0]),
        'story_author' : story_details[1],
        'story_date' : story_details[2],
        'story_twitter' : story_details[3],
        'story_keywords' : story_details[4],
    }

    return story_dic

def get_articles(story_loc, html_loc, date_today, logger, domain_list = None):
    '''
    Function that will load in the pickle, use the link to find where the HTML is found, and then pull 
    the key features from the article page (like the actual article text)
    '''
    bad_links = []

    if domain_list is None:
        domain_list = os.listdir(story_loc)

    # Start by looping over the pickles we have saved
    for domain in domain_list:
        pickle_loc = os.path.join(story_loc,domain, date_today)
        pickle_files = os.listdir(pickle_loc)

        logger.info('Reading stories from {} pickles for {}'.format(len(pickle_files), domain))
        for pickle_file in pickle_files:
            pickle_path = os.path.join(pickle_loc, pickle_file)
            logger.debug('Loading the story pickle found at \n{}'.format(pickle_file))
            
            # First load the pickle
            with open(pickle_path, 'rb') as article_file:
                article_content = pickle.load(article_file)
            
            # Check the URL and then get the HTML path
            valid_url = re.match('^http\S*www\.\S*$', article_content['article_link'])
            
            if valid_url and 'fake_link' not in article_content['article_link']:  
                url_extension = re.search('[^\/]\/([^\/][^www].*)', valid_url.group(0)).group(1).replace('/', '_')
                story_html = re.sub('[^A-z0-9_]+', '', url_extension)
                logger.debug('Found the link\n{}'.format(article_content['article_link']))

                # Convert into the direct location
                story_path = os.path.join(html_loc, domain, date_today, 'story_link', story_html + '.html')

                # Load the HTML
                logger.debug('Getting story for HTML located at \n{}'.format(story_path))
                try:
                    # Then pull the info
                    story_text = get_story(story_path, domain, logger)

                    # Attach to our dictionary
                    article_content['story_text'] = story_text['story_text']
                    article_content['story_author'] = story_text['story_author']
                    article_content['story_date'] = story_text['story_date']
                    article_content['story_twitter'] = story_text['story_twitter']
                    article_content['story_keywords'] = story_text['story_keywords']

                    # And then save it again
                    logger.debug('Overwriting the pickle at \n{}'.format(pickle_file))
                    with open(pickle_path, 'wb') as article_file:
                        pickle.dump(article_content, article_file)
                        
                except Exception as e:
                    logger.error('Error getting the story')
                    logger.error(e)
                    bad_links.append(article_content['article_link'])
            else:
                logger.warning('The URL is not valid:\n{}'.format(article_content['article_link']))
                bad_links.append(article_content['article_link'])

    if len(bad_links) != 0:
        logger.warning('Have found {} bad links'.format(len(bad_links)))
    
    return bad_links