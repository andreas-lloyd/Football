import pandas as pd
import spacy

# Set up the extraction parameters
DISABLE = ['parser', 'ner', 'textcat', 'tokenizer', 'tagger']
nlp = spacy.load('en_core_web_lg', disable=DISABLE)
REGEX_STRING = r'([A-ZÁÉÍÓÚÑ]+[A-záéíóúñÁÉÍÓÚÑ-]+(?: [A-ZÁÉÍÓÚÑ]+[A-záéíóúñÁÉÍÓÚÑ-]+)*)'

def extract_entities(article_titles):
    """
    Takes a DF series of article titles and applies the regex to it

    Main issue is that we are able to reject stopwords but not other generic words

    We could invent some logic that we are not allowed to insert a new entry if that was the first entity of an article
    This could work OK since we should be doing some form of normalisation to see if we add a new one to the unique set anyways
    """

    # Use the regex extract to get all the matcheswith the regex, and then group on the index of the column to get all results into a list
    article_matches = pd.DataFrame(article_titles.str.extractall(REGEX_STRING).reset_index().groupby('level_0')[0].apply(lambda x: x.tolist()))

    # Then search this to see if we have some basic words that we don't want to include as an entity
    match_list = article_matches[0].tolist()
    article_matches['article_entities'] = [[entity for entity in story if entity.lower() not in nlp.Defaults.stop_words] for story in match_list]

    return article_matches