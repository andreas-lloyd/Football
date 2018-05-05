import re, os, datetime, pickle, pandas as pd
import football_functions.source_specific.bbc.process_html as bbc # then bbc.process_html.XXX
import football_functions.source_specific.dailymail.process_html as dailymail
import football_functions.source_specific.mirror.process_html as mirror
import football_functions.source_specific.guardian.process_html as guardian
import football_functions.source_specific.skysports.process_html as skysports
import football_functions.source_specific.telegraph.process_html as telegraph

from football_functions.source_specific.bbc import process_html as bbc
from football_functions.source_specific.dailymail import process_html as dailymail
from football_functions.source_specific.guardian import process_html as guardian
from football_functions.source_specific.mirror import process_html as mirror
from football_functions.source_specific.skysports import process_html as skysports
from football_functions.source_specific.telegraph import process_html as telegraph

def check_html(check_1, check_2, domain, is_sublinks, logger):
    '''
    Function to check if 2 HTMLs are the same by doing some set operations
    '''
    
    # If looking at sublinks then pull the links
    if is_sublinks:
        # Now do source specific stuff
        if domain == 'bbc':
            modifier = 'football_teams' in check_1
            articles_info_1 = bbc.extract_headlines(check_1, modifier, logger)
            articles_info_2 = bbc.extract_headlines(check_2, modifier, logger)

        elif domain == 'dailymail':
            modifier = 'football_index' not in check_1
            articles_info_1 = dailymail.extract_headlines(check_1, modifier, logger)
            articles_info_2 = dailymail.extract_headlines(check_2, modifier, logger)

        elif domain == 'theguardian':
            articles_info_1 = guardian.extract_headlines(check_1, logger)
            articles_info_2 = guardian.extract_headlines(check_2, logger)

        elif domain == 'mirror':
            articles_info_1 = mirror.extract_headlines(check_1, logger)
            articles_info_2 = mirror.extract_headlines(check_2, logger)

        elif domain == 'skysports':
            modifier = 'regional' in check_1
            articles_info_1 = skysports.extract_headlines(check_1, modifier, logger)
            articles_info_2 = skysports.extract_headlines(check_2, modifier, logger)

        elif domain == 'telegraph':
            articles_info_1 = telegraph.extract_headlines(check_1, logger)
            articles_info_2 = telegraph.extract_headlines(check_2, logger)
        
        # Compare on the title and link of the article
        return articles_info_1 == articles_info_2
        #return articles_info_1['article_title'] == articles_info_2['article_title'] and articles_info_1['article_link'] == articles_info_2['article_link']
    
    else:
        # Else we are looking at stories - will just get the actual text
        if domain == 'bbc':
            story_details_1 = bbc.get_text(check_1, logger)[0]
            story_details_2 = bbc.get_text(check_2, logger)[0]

        elif domain == 'dailymail':
            story_details_1 = dailymail.get_text(check_1, logger)[0]
            story_details_2 = dailymail.get_text(check_2, logger)[0]

        elif domain == 'theguardian':
            story_details_1 = guardian.get_text(check_1, logger)[0]
            story_details_2 = guardian.get_text(check_2, logger)[0]

        elif domain == 'mirror':
            story_details_1 = mirror.get_text(check_1, logger)[0]
            story_details_2 = mirror.get_text(check_2, logger)[0]

        elif domain == 'skysports':
            story_details_1 = skysports.get_text(check_1, logger)[0]
            story_details_2 = skysports.get_text(check_2, logger)[0]

        elif domain == 'telegraph':
            story_details_1 = telegraph.get_text(check_1, logger)[0]
            story_details_2 = telegraph.get_text(check_2, logger)[0]
        
        return story_details_1 == story_details_2
        

def check_same(f_name, path_1, path_2, is_pickle, domain, logger):
    '''
    A function to check if the content found at path_1 and path_2 is the same - note that we 
    already assume the file names are the same, because only call them in those circumstances
    If we are looking at pickles, need to set is_pickle to True and do a pickle load
    '''
    check_1 = os.path.join(path_1, f_name)
    check_2 = os.path.join(path_2, f_name)
    
    if is_pickle:
        with open(check_1, 'rb') as content_1:
            with open(check_2,'rb') as content_2:
                return pickle.load(content_1) == pickle.load(content_2)
    else:
        is_sublinks = 'sublinks' in check_1
        return check_html(check_1, check_2, domain, is_sublinks, logger)

def try_candidates(deletion_candidates, is_pickle, logger, domain, deletion_log = None):
    '''
    A function to try the candidates to see if they have the same content - and then delete or not accordingly
    Will return a frame with the deleted files (to remove from our potential files) and the log, which has been updated
    Note that we feed in the deletion log to update it - but if we feed "None", it does not get updated
    '''
    # Can't find a way to do this by the column names - so will get indices
    pf_index = deletion_candidates.columns.get_loc('Potential_file')
    pp_index = deletion_candidates.columns.get_loc('Potential_path')
    fp_index = deletion_candidates.columns.get_loc('File_path')
    
    # Then get whether or not we should delete them
    logger.info('Will check {} files to see if they are the same'.format(deletion_candidates.shape[0]))
    deletion_candidates['Delete'] = deletion_candidates.apply(lambda x: check_same(x[pf_index], x[pp_index], x[fp_index], is_pickle, domain, logger), axis = 1)
    
    # Delete those that we should
    logger.info('Have found {} files that will be deleted'.format(deletion_candidates['Delete'].sum()))
    deletion_candidates[deletion_candidates['Delete']].apply(lambda x: os.remove( os.path.join(x[pp_index], x[pf_index])), axis = 1)
    
    # Then we need to update the deletion log
    if deletion_log is not None:
        # Pull the name and path, and add whether or not we are dealing with pickles
        new_entries = deletion_candidates.loc[deletion_candidates['Delete'], ['File_name', 'File_path']]
        new_entries['Is_pickle'] = is_pickle
        
        # Then append to end
        deletion_log = deletion_log.append(new_entries)
    
    # Finally return the ones we deleted and the log that has been updated
    return deletion_candidates[deletion_candidates['Delete']], deletion_log

def delete_duplicates(search_loc, date_today, mode, is_pickle, past_deletions, logger):
    '''
    Function for looking at currently saved files and delete them if they are duplicates of something already seen
    This will be carried out after saving HTML and getting headlines - focusing on not having to pull more HTML than necessary
    Search_loc is the key argument and should point directly to suburls, story_links, or pickle stories - search_loc/date/mode
    Past deletions should be a directory to where the deletions are located
    '''
    logger.info('Looking for files in:\n{}'.format(search_loc))
    
    deletion_log = pd.read_csv(past_deletions)

    # Search ever domain in the directory given to search through
    for domain in os.listdir(search_loc):
        logger.info('Looking at {}'.format(domain))
        
        date_loc = os.path.join(search_loc, domain, date_today, mode)
        
        # It is possible that for some domains we don't have this path
        if os.path.exists(date_loc):    
            # The first part of the process is to grab all of the potential files up for deletion
            file_frame = pd.DataFrame({'Potential_file' : os.listdir(date_loc), 'Potential_path' : date_loc})
            
            logger.info('Will be looking at {} files'.format(file_frame.shape[0]))
            
            # Now the process of deletion is to look at the past deletions (if any) and then all dates that came before        
            if deletion_log.shape[0] != 0:
                # Look at past deletions to do a quick compare and delete - do this by merging on file names
                deletion_candidates = file_frame.merge(deletion_log[deletion_log['Is_pickle'] == is_pickle], left_on = 'Potential_file', right_on = 'File_name')
                num_log_delete = deletion_candidates.shape[0]
                
                logger.info('Have found {} candidates to delete from our log'.format(num_log_delete))
                
                # So if we have something here, will delete, but won't update our log
                if num_log_delete != 0:
                    deleted_candidates, _ = try_candidates(deletion_candidates, is_pickle, logger, domain)
                    
                    # Once we have deleted, will remove those files from our original list
                    file_frame = file_frame[~ file_frame['Potential_file'].isin(deleted_candidates['Potential_file'])]
                    
                    logger.info('After deletion now have {} files left'.format(file_frame.shape[0]))
            
            # Then we will search through previous dates in that domain
            domain_loc = os.path.join(search_loc, domain)
            possible_dates = os.listdir(domain_loc)
            valid_dates = sorted([possible_date for possible_date in possible_dates if datetime.datetime.strptime(possible_date, '%Y_%m_%d') < datetime.datetime.strptime(date_today, '%Y_%m_%d')])
            
            logger.info('Have found {} dates to search through'.format(len(valid_dates)))
            
            # Now we will loop through the dates and do a similar thing to the deletion log
            for deletion_date in valid_dates:
                logger.info('Now searching date {}'.format(deletion_date))
                delete_path = os.path.join(search_loc, domain, deletion_date)
                
                # Since we don't have a deletion log, make a "check" frame
                check_frame = pd.DataFrame({'File_name' : os.listdir(delete_path), 'File_path' : delete_path, 'Is_pickle' : is_pickle})
                
                logger.info('Comparing against {} files'.format(check_frame.shape[0]))
                
                # Then follow the same process and get the candidates
                deletion_candidates = file_frame.merge(check_frame, left_on = 'Potential_file', right_on = 'File_name')
                num_date_delete = deletion_candidates.shape[0]

                # Then delete
                logger.info('Have found {} candidates to delete from {}'.format(num_date_delete, deletion_date))

                # Again we dive in if we have found some candidates, but this time updating the log
                if num_date_delete != 0:
                    deleted_candidates, deletion_log = try_candidates(deletion_candidates, is_pickle, logger, domain, deletion_log)

                    # And finally remove like before
                    file_frame = file_frame[~ file_frame['Potential_file'].isin(deleted_candidates['Potential_file'])]
                    logger.info('After deletion now have {} files left'.format(file_frame.shape[0]))