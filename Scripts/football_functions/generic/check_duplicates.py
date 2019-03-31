"""
2019-03-31: change - as moving to save all in one, need to make this check some global list for things that we have already done

Think will make this script build up a log that is only run once for each execution (will have to be careful in multiprocess - or can do once for each domain)
and then check that list - will avoid having to update something

Will also make it look back at regular files to build this list, just to have backwards compatibility
"""

import re
import json

def find_articles(search):
    """
    Small wrapper to get the names of all articles from link
    """
    with search.open() as json_file:
        return json.load(json_file)['names']

def check_duplicates(article_link, domain_path, search_list):
    """
    Function for checking if we have seen the file before - we do this by checking
    a search list that is built up if an empty list is given to it

    This should be called for each article, but we can skip the process of the search list by feeding it back in
    """
    # Start building the file name out of the link, checking that everything is valid         
    url_reg = re.search('\/([^\/][^www].*)', article_link)

    # Sometimes get weird URLs of other websites
    if url_reg:
        url_extension = url_reg.group(1).replace('/', '_')
    else:
        url_extension = re.sub('[^A-z0-9]', '_', article_link)

    article_name = re.sub('[^A-z0-9_]+', '', url_extension)

    # Now want to build up this list of things we have searched - only build if we are given a blank
    if len(search_list) == 0:
        to_search = domain_path.glob('*/*/*/*.json')
        for search in to_search:
            if 'all_stories.json' not in str(search):
                search_list.append(search.stem)
            else:
                search_list.extend(find_articles(search))

    # Now we can just check this list and return stfuff
    if 'fake_link' not in article_name:
        return article_name in search_list, article_name, search_list
    else:
        return False, article_name, search_list