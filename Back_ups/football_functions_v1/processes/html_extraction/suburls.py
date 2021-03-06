'''
Functions that will follow the process for analysing the suburls found in the baseurls
'''
import os
from football_functions.generic import pull_html
import football_functions.source_specific.bbc.process_html as bbc
import football_functions.source_specific.dailymail.process_html as dailymail
import football_functions.source_specific.mirror.process_html as mirror
import football_functions.source_specific.guardian.process_html as guardian

def extract_urls(html_loc, organ_loc, date_today, domain_list = None):
    '''
    Function that will extract the suburls from the HTML found in the baseurls
    Takes the location of /Data/HTML and Data/Organisation
    '''

    if domain_list is None:
        domain_list = os.listdir(html_loc)

    # Start by looping over all the domains we find in the HTML data folder
    for domain in domain_list:
        print('Now looking at sources from {}'.format(domain))

        # We will then loop over all the HTML we find there to start pulling those URLs
        search_path = html_loc + domain + '/' + date_today + '/' + 'base_urls'
        for html_file in os.listdir(search_path):
            html_path = search_path + '/' + html_file
            links = []
            
            # Will only process certain URLsfor each domain
            if domain == 'bbc' and 'teams' in html_file:
                links.extend(bbc.get_suburls(html_path))

            if domain == 'dailymail' and 'sport_football' in html_file:
                links.extend(dailymail.get_suburls(html_path))

            if domain == 'mirror'  and 'sport_football' in html_file:
                links.extend(mirror.get_suburls(html_path))

            if domain == 'theguardian'  and 'teams' in html_file:
                links.extend(guardian.get_suburls(html_path))

            # If we have found some links then print them to file in organ_loc
            if len(links) != 0:
                print('Have found {} links from {}'.format(len(links), domain))
                sublinks_path = organ_loc + domain + '/' + date_today + '/'
                
                # Check if exists
                if not os.path.exists(sublinks_path):
                    print('Making directory {}'.format(sublinks_path))
                    os.makedirs(sublinks_path)
                
                print('Writing links file')
                with open(sublinks_path + 'sublinks.txt', 'w') as sublink_file:
                    for link in links:
                        sublink_file.write('{}\n'.format(link))
                        
                print('Finished writing to file\n')

def scrape_urls(organ_loc, html_loc, date_today, proxy):
    '''
    Function that will scrape the suburls found in the baseurls and then save the HTML
    So this is executed after the extract_urls function on the links that were saved
    '''
    error_report = []
    mode = 'sublinks'

    # Start by looping the domains we find in the organisation folder - ignoring any non directories
    for domain in [domain for domain in os.listdir(organ_loc) if '.' not in domain]:
        sublink_path = organ_loc + domain + '/' + date_today + '/sublinks.txt'

        with open(sublink_path, 'r') as sublink_file:
            for url in sublink_file.readlines():
                error_report.append(pull_html.process_url(url.rstrip(), html_loc, mode, date_today, proxy))
    
    num_urls = len(error_report)
    num_failed = len([(url, error) for url, error in error_report if error != 'No error'])
    print('Finished reading {} URLs, of which {} failed'.format(num_urls, num_failed))

    return error_report