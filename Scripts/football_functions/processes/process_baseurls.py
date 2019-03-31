"""
In this script we carry out thefull process for the baseurls, from getting the suburls and then finally saving the content in jsons

2019-03-31: change, will make everything save in one, but will have to alter the check duplicates part - maybe save json that has stories and what have saved
                    will also have to run back track script to make sure that on the next run we don't just download everything
"""
import re, json
from football_functions.generic import pull_html as ph
from football_functions.generic import check_duplicates as cd
from football_functions.processes import process_suburls as ps

def full_process(baseurl_loc, proxy, logger, save_path, date_today):
    """
    A function that will carry out the full, reduced process of getting the stories
    """
    logger.info('BASEURL    Loading in the base URLs...')
    baseurl_list = []

    if 'http' not in str(baseurl_loc):
        with baseurl_loc.open(mode = 'r') as list_file:
            for url in list_file.readlines():
                baseurl_list.append(url.rstrip())
    else:
        baseurl_list = [str(baseurl_loc)]
            
    logger.info('BASEURL    Have found {}'.format(len(baseurl_list)))
        
    # We loop over the loaded in base urls
    print('Starting to process base urls')
    for base_url in baseurl_list:
        # Get the domain for source specific stuff
        domain = re.search('^.*www\.(.*?)\..*', base_url).group(1)
        print('Looking at stories from {}'.format(domain))
                
        # Just start a log to get things going
        logger.info('BASEURL    Starting the process for {} which is from {}'.format(base_url, domain))
        
        try:
            # Get the HTML for that URL - first scrape
            baseurl_html = ph.process_url(base_url, proxy, logger)

            if baseurl_html[1] != 'No error':
                logger.error('BASEURL    Have found an error in the baseline HTML')
                pass
            
            # Then we will feed it into the suburl extractor
            logger.info('BASEURL    Finding the suburls')
            suburl_list = ps.find_suburls(baseurl_html[0], base_url, domain, logger)

            # Init some lists so that we can save everything in the same place
            headlines = {'stories' : [], 'names' : []}
            search_list = []
            
            # So we loop over the sub_urls that we found, pull the HTML and then pull out the headlines - second scrape
            for sub_url in suburl_list:

                try:
                    suburl_html = ph.process_url(sub_url, proxy, logger)
                    
                    if suburl_html[1] != 'No error':
                        logger.error('SUBURL    Have found an error in the suburl HTML for {}'.format(sub_url))
                        continue
                    
                    # Now pull out the headlines - HAVE TO CHECK WHAT HAPPENS TO SPECIAL NON-SUBURL TYPE LINKS
                    suburl_headlines = ps.extract_headlines(suburl_html[0], sub_url, domain, logger)
                    
                    # Now we should loop over the headlines and pull out the story - finally saving
                    logger.info('SUBURL    Now looking at the headlines')
                    for headline_id in suburl_headlines:
                        headline = suburl_headlines[headline_id]
                        
                        try:
                            # Before doing anything - want to make sure that the headline is not a duplicate - also check own directory
                            is_duplicate, article_name, search_list = cd.check_duplicates(headline['article_link'], save_path / domain, search_list)
                            
                            # Want to check if duplicate OR if we already added this one, to avoid scraping again
                            if is_duplicate or (article_name not in headlines['names'] and 'fake_link' not in article_name):
                                logger.warning('HEADLINE    Have found a duplicate link for file named {}'.format(article_name))
                                continue
                            
                            # First step for good headlines is to pull the HTML - third scrape
                            story_html = ph.process_url(headline['article_link'], proxy, logger)
                            
                            if story_html[1] != 'No error' and story_html[1] != 'Fake link':
                                logger.error('HEADLINE    Have found an error in the story HTML for {}'.format(headline['article_link']))
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

                            # And save result to list for saving later ut only if not already there
                            if headline not in headlines:
                                headlines['stories'].append(headline)
                                headlines['names'].append(article_name)
                            else:
                                logger.warning('HEADLINE    Have found the headline already for file called {}'.format(article_name))
                        
                        except (KeyboardInterrupt, SystemExit):
                            raise
                        except:
                            logger.error('HEADLINE    An error has occurred in headline with link {}:\n'.format(headline['article_link']))
                            logger.error(error)

                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as error:
                    logger.error('SUBURL    An error has occurred in suburl {}:\n'.format(sub_url))
                    logger.error(error)

            # Build up our story path where we will save it
            baseurl_path = save_path / domain / date_today

            # Now we can check if the directory exists
            if not baseurl_path.exists():
                baseurl_path.mkdir(parents = True)

            # And save the file to json
            baseurl_file = baseurl_path / 'all_stories.json'
            with baseurl_file.open(mode = 'w') as json_file:
                json.dump(headlines, json_file, indent = 4)

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as error:
            logger.error('BASEURL    An error has occurred in baseurl {}:\n'.format(base_url))
            logger.error(error)