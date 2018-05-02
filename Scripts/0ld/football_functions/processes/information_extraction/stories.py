'''
Functions to scrape the links found in the articles from the earlier script
'''
import pickle, os
from football_functions.generic import pull_html

def process_articles(story_loc, html_loc, date_today, proxy):
    '''
    Function to grab all of the articles and begin processing them
    Note that since this process is so long - will do two loops 
    This is useful for if the internet drops temporarily
    '''
    # Will save the links that do not work for analysis later
    failed_links = []
    mode ='story_link'

    # Loop over domains and the pickles we find there
    for domain in os.listdir(story_loc):
        pickle_loc = story_loc + domain + '/' + date_today + '/'
        for pickle_file in os.listdir(pickle_loc):
            # Load the pickle
            with open(pickle_loc + pickle_file, 'rb') as article_file:
                article_content = pickle.load(article_file)

            # Send the link to be pulled and receive the error type
            error_report = pull_html.process_url(article_content['article_link'], html_loc, mode, date_today, proxy, domain)

            # If we have an error - will append to list to process later
            if error_report[1] != 'No error':
                failed_links.append(error_report)

    print('Finished initial run with {} links that have errors'.format(len(failed_links)))

    # Then process again those that failed
    bad_links = []
    for domain in os.listdir(story_loc):
        for failed_link in failed_links:
            print('Now looking again at link \n{}'.format(failed_link[0]))

            # Will not look at file errors
            if failed_link[1] != 'File error':
                print('Not a file error - trying to pull HTML again')

                error_report = pull_html.process_urls(failed_link[0], html_loc, mode, date_today, proxy, domain)

                if error_report[1] != 'No error':
                    bad_links.append(error_report)

    print('Finished second run with {} links that are bad'.format(len(bad_links)))

    return bad_links