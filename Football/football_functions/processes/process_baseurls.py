"""
In this script we carry out thefull process for the baseurls, from getting the suburls and then finally saving the content in jsons
"""
import re, json
from football_functions.generic import pull_html as ph
from football_functions.generic import check_duplicates as cd
from football_functions.processes import process_suburls as ps

def full_process(baseurl_loc, proxy, logger, save_path, date_today):
    """
    A function that will carry out the full, reduced process of getting the stories
    """
    logger.info('Loading in the base URLs...')
    baseurl_list = []
    with baseurl_loc.open(mode = 'r') as list_file:
        for url in list_file.readlines():
            baseurl_list.append(url.rstrip())
            
    logger.info('Have found {}'.format(len(baseurl_list)))
        
    # We loop over the loaded in base urls
    print('Starting to process base urls')
    for base_url in baseurl_list:
        # Get the domain for source specific stuff
        domain = re.search('^.*www\.(.*?)\..*', base_url).group(1)
        print('Looking at stories from {}'.format(domain))
                
        # Just start a log to get things going
        logger.info('Starting the process for {} which is from {}'.format(base_url, domain))
        
        # Get the HTML for that URL - first scrape
        baseurl_html = ph.process_url(base_url, proxy, logger)

        if baseurl_html[1] != 'No error':
            logger.warning('Have found an error in the baseline HTML')
            pass
        
        # Then we will feed it into the suburl extractor
        logger.info('Finding the suburls')
        suburl_list = ps.find_suburls(baseurl_html[0], base_url, domain, logger)
        
        # So we loop over the sub_urls that we found, pull the HTML and then pull out the headlines - second scrape
        for sub_url in suburl_list:
            suburl_html = ph.process_url(sub_url, proxy, logger)
            
            if suburl_html[1] != 'No error':
                logger.warning('Have found an error in the suburl HTML for {}'.format(sub_url))
                continue
            
            # Now pull out the headlines - HAVE TO CHECK WHAT HAPPENS TO SPECIAL NON-SUBURL TYPE LINKS
            suburl_headlines = ps.extract_headlines(suburl_html[0], sub_url, domain, logger)
            
            # Now we should loop over the headlines and pull out the story - finally saving
            logger.info('Now looking at the headlines')
            for headline_id in suburl_headlines:
                headline = suburl_headlines[headline_id]
                
                # Beforedoing anything - want to make sure that the headline is not a duplicate - also check own directory
                is_duplicate, json_name = cd.check_duplicates(headline['article_link'], save_path / domain)
                
                story_path = save_path / domain / date_today
                story_file = story_path / json_name
                
                if is_duplicate or story_file.exists():
                    logger.warning('Have found a duplicate link for file named {}'.format(json_name))
                    continue
                
                # First step for good headlines is to pull the HTML - third scrape
                story_html = ph.process_url(headline['article_link'], proxy, logger)
                
                if story_html[1] != 'No error' and story_html[1] != 'Fake link':
                    logger.warning('Have found an error in the story HTML for {}'.format(headline['article_link']))
                    continue
                
                # Then get the text
                if story_html[1] != 'Fake link':
                    story_details = ps.get_story(story_html[0], domain, logger)
                    
                    # Add on to our headline
                    headline['story_text'] = story_details['story_text']
                    headline['story_author'] = story_details['story_author']
                    headline['story_date'] = story_details['story_date']
                    headline['story_twitter'] = story_details['story_twitter']
                    headline['story_keywords'] = story_details['story_keywords']
                else:
                    # If it is fake, then fill in with blanks
                    headline['story_text'] = ''
                    headline['story_author'] = ''
                    headline['story_date'] = ''
                    headline['story_twitter'] = ''
                    headline['story_keywords'] = ''

                # And finally create directory and save       
                if not story_path.exists():
                    story_path.mkdir(parents = True)
                
                with story_file.open(mode = 'w') as json_file:
                    json.dump(headline, json_file, indent = 4)