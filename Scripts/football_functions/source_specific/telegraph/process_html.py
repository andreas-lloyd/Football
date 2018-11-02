'''
Functions included
- Find headlines
- Find stories
'''
import parsel as pr

def extract_headlines(html_content, logger):
    '''
    Extraction of headlines from Telegraph HTML
    '''

    sel = pr.Selector(html_content)
    articles_info = {}
    
    # This will absorb some others that are fantasy football - so do a check on the URL
    articles = sel.xpath('//li[@class = "list-of-entities__item "]/div/a[contains(@href, "/football/")]')
    
    article_titles = articles.xpath('..//h3/a/text()').extract()
    article_links = articles.xpath('./@href').extract()
    article_summaries = ''
    article_images = articles.xpath('./div/@data-alt').extract()
    article_dates = articles.xpath('..//time/@datetime').extract()
    
    # Now combine into dictionaries
    for i, title in enumerate(article_titles):
        
        # Fix article links
        if '://www' not in article_links[i]:
            article_links[i] = 'http://www.telegraph.co.uk' + article_links[i]

        article_info = {
            'article_title' : title.strip(),
            'article_link' : article_links[i],
            'article_summary' : article_summaries,
            'article_image' : article_images[i],
            'article_date' : article_dates[i]
        }

        articles_info['article_{}'.format(i + 1)] = article_info

    return articles_info

def get_text(html_content, logger):
    '''
    Function that will retrieve the story text from HTML
    NOTE that must do in order
    text, author, date, twitter, keywords
    '''

    sel = pr.Selector(html_content)

    # Get the main text - and then join everything up - note that join on blank to replace with . later
    story_body = sel.xpath('//p//text()').extract()
    story_text = ''.join(story_body)

    # Author and date are blank
    story_author = ''
    story_date = ''

    story_twitter = sel.xpath('//meta[@name = "twitter:description"]/@content').extract_first()
    story_keywords = sel.xpath('//meta[@name = "keywords"]/@content').extract()

    # Return in this order specifically
    return story_text, story_author, story_date, story_twitter, story_keywords