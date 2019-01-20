'''
Functions included
- Find sublinks
- Find headlines
- Find stories
'''
import parsel as pr

def get_suburls(html_content, logger):
    '''
    Function that will get the suburls from the passed HTML
    '''
    
    sel = pr.Selector(html_content)
    
    return sel.xpath('//div[not(contains(@data-reactid, "group_0"))]/ul/li/a[@class = "gs-o-list-ui__link sp-c-group-index__link gel-pica-bold"]/@href').extract()

def extract_headlines(html_content, modifier, logger):
    '''
    Returns a dictionary with the key aspects of BBC headlines
    We have two types - the team pages and the confirmed transfers
    In the team pages - we have an image which also has a title (could be useful). 
    Each article is separated into "article" blocks and the URLs are non-absolute with a numeric code
    Could potentially improve timing here as the loops might be excessive
    '''    
    
    sel = pr.Selector(html_content)
    articles_info = {}
    
    if modifier:
        # Get the article information - write an initial search and then find ANYTHING inside
        search = '//article[@class = "clearfix faux-block-link lakeside lakeside--auto lakeside--has-media"]'
        articles = sel.xpath(search)
        
        # Need to loop because we want all the info to match up - even if not present
        for i, article in enumerate(articles):
            
            # Step through each article and extract_first to only return value and not list
            article_title = article.xpath('.//span[@class = "lakeside__title-text"]/text()').extract_first()
            article_link = article.xpath('.//a[@class = "faux-block-link__overlay"]/@href').extract_first()
            article_summary = article.xpath('.//p/text()').extract_first()
            article_image = article.xpath('.//img/@alt').extract_first()
            article_date = article.xpath('.//span[@class = "timestamp"]/time/text()').extract_first()
            
            if article_summary:
                article_summary = article_summary.strip()
            
            if '://www' not in article_link:
                article_link = 'http://www.bbc.com' + article_link
            
            article_info = {
                'article_title' : article_title.strip(),
                'article_link' : article_link,
                'article_summary' : article_summary,
                'article_image' : article_image,
                'article_date' : article_date
            }
            
            articles_info['article_{}'.format(i + 1)] = article_info
    
    else:
        article_titles = sel.xpath('//p/a/text()').extract()
        article_links = sel.xpath('//p/a/@href').extract()
        article_summaries = sel.xpath('//p/text()').extract()
        article_images = ''
        article_dates = ''
        
        # Now combine into dictionaries like above
        for i, title in enumerate(article_titles):
            
            if article_summaries[i]:
                article_summaries[i] = article_summaries[i].strip()
            
            if 'http://' not in article_links[i] and 'https://' not in article_links[i]:
                article_links[i] = 'http://www.bbc.com' + article_links[i]
            
            article_info = {
                'article_title' : title.strip(),
                'article_link' : article_links[i],
                'article_summary' : article_summaries[i],
                'article_image' : article_images,
                'article_date' : article_dates
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
    story_body = sel.xpath('//p//text() | //figcaption/text()').extract()
    story_text = ''.join(story_body)

    story_author = sel.xpath('//p[@class = "gel-long-primer"]/text()').extract_first()

    story_date = sel.xpath('//meta[@property = "rnews:datePublished"]/@content').extract_first()
    
    # Rest are blank 
    story_twitter = ''
    story_keywords = [''] 

    # Return in this order specifically
    return story_text, story_author, story_date, story_twitter, story_keywords