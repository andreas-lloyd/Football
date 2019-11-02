from collections import Counter
import pandas as pd
import nltk

def cloud_n_count(text_list, most_common = 10, vocab_name = None, n_gram = None, most_common_ng = 10, ngram_file = None, get_wc = False):
    '''
    Wrapper to get word cloud and word counts for basic analysis - can also give n_gram argument to check for bigrams etc
    '''
    
    # Split list of words into separate words and get counter
    word_list = [word for text in text_list for word in nltk.tokenize.wordpunct_tokenize(text)]
    word_count = Counter(word_list)
    
    print('The {} most common words are the following:'.format(most_common))
    print(word_count.most_common(most_common))
    
    # Save the vocabulary to file
    if vocab_name:
        count_frame = pd.DataFrame(word_count.most_common(len(word_count)), columns = ['Word', 'Count'])
        
        count_frame.to_excel(vocab_name, index = False)
        
    # Then for ngrams as well
    if n_gram:
        # For each text, split it up into list of words, get those ngrams, then put into a long list
        text_ngrams = [text_ngram for text in text_list for text_ngram in list(nltk.ngrams(nltk.tokenize.wordpunct_tokenize(text), n_gram))]
        ngram_count = Counter(text_ngrams)
        
        print('\nThe {} most common ngrams are the following:'.format(most_common_ng))
        print(ngram_count.most_common(most_common_ng))
    
    # And finally get the wordcloud
    if get_wc:
        get_wordcloud(text_list)
    
    if n_gram:
        ngrame_frame = pd.DataFrame(ngram_count.most_common(len(ngram_count)), columns = ['Word', 'Count'])
        
        # Save those with more than 2 counts to file - will treat it a bit too
        if ngram_file:
            save_frame = ngrame_frame.loc[ngrame_frame['Count'] > 1, :]
            
            # Need to split the tuple into multiple and fix up names
            col_names = ['Word_' + str(i + 1) for i in range(n_gram)]
            save_frame[col_names] = save_frame['Word'].apply(pd.Series)
            save_frame[col_names + ['Count']].to_excel(ngram_file, index = False)
        
        return word_count, ngrame_frame
    else:
        return word_count