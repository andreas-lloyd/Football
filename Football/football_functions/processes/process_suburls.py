"""
In this script we include the functions that work to find the suburls, then process the HTML contained within for headlines, and finally those stories
"""
import football_functions.source_specific.bbc.process_html as bbc
import football_functions.source_specific.dailymail.process_html as dailymail
import football_functions.source_specific.mirror.process_html as mirror
import football_functions.source_specific.guardian.process_html as guardian
import football_functions.source_specific.skysports.process_html as skysports
import football_functions.source_specific.telegraph.process_html as telegraph
import re

def find_suburls(baseurl_html, base_url, domain, logger):
    """
    Function that will return to us all of the suburls on the page we just downloaded
    """
    links = []

    # Will only process certain URLsfor each domain
    if domain == 'bbc' and 'teams' in base_url:
        links.extend(bbc.get_suburls(baseurl_html, logger))

    elif domain == 'dailymail' and 'sport/football' in base_url:
        links.extend(dailymail.get_suburls(baseurl_html, logger))

    elif domain == 'mirror'  and 'sport/football' in base_url:
        links.extend(mirror.get_suburls(baseurl_html, logger))

    elif domain == 'theguardian'  and 'teams' in base_url:
        links.extend(guardian.get_suburls(baseurl_html, logger))
    else:
        # If we are here then it should not be a suburl and we would just scrape directly
        logger.info('Returning the original URL as only suburl')
        links = [base_url]
    
    if len(links) == 0:
        logger.warning('Have found {} links from {}'.format(len(links), domain))
    
    return links


def extract_headlines(suburl_html, sub_url, domain, logger):
    """
    Function that will extract headlines from the HTML previously downloaded for suburls
    """
    
    # Now do source specific stuff
    if domain == 'bbc':
        modifier = 'football/teams' in sub_url
        articles_info = bbc.extract_headlines(suburl_html, modifier, logger)

    elif domain == 'dailymail':
        modifier = 'football/index' not in sub_url
        articles_info = dailymail.extract_headlines(suburl_html, modifier, logger)
        
    elif domain == 'theguardian':
        articles_info = guardian.extract_headlines(suburl_html, logger)
        
    elif domain == 'mirror':
        articles_info = mirror.extract_headlines(suburl_html, logger)
    
    elif domain == 'skysports':
        modifier = 'regional' in sub_url
        articles_info = skysports.extract_headlines(suburl_html, modifier, logger)
        
    elif domain == 'telegraph':
        articles_info = telegraph.extract_headlines(suburl_html, logger)

    return articles_info

def get_story(story_html, domain, logger):
    """
    Function to take the HTML and then get the story text according to the domain
    """

    if domain == 'bbc':
        story_details = bbc.get_text(story_html, logger)

    elif domain == 'dailymail':
        story_details = dailymail.get_text(story_html, logger)

    elif domain == 'theguardian':
        story_details = guardian.get_text(story_html, logger)

    elif domain == 'mirror':
        story_details = mirror.get_text(story_html, logger)

    elif domain == 'skysports':
        story_details = skysports.get_text(story_html, logger)

    elif domain == 'telegraph':
        story_details = telegraph.get_text(story_html, logger)

    story_dic = {
        'story_text' : re.sub('([a-z0-9])([A-Z])', r'\1.\2', story_details[0]),
        'story_author' : story_details[1],
        'story_date' : story_details[2],
        'story_twitter' : story_details[3],
        'story_keywords' : story_details[4],
    }

    return story_dic