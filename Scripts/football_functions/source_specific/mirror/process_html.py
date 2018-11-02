'''
Functions included
- Find sublinks
- Find headlines
- Find stories
'''
import parsel as pr

def get_suburls(html_content, logger):
    
    sel = pr.Selector(html_content)
    
    links = sel.xpath('//a[contains(@class, "badge")]/@href').extract()
    return ['http://www.mirror.co.uk' + link for link in links]

def extract_headlines(html_content, logger):
    '''
    Extract headlines from Mirror HTML content
    '''

    sel = pr.Selector(html_content)
    articles_info = {}
    
    
    # Note that we can get headline descriptions even though not present on page - seems all page styles are the same
    article = sel.xpath('//div[@class = "teaser"]')

    article_titles = article.xpath('.//strong/a/text()').extract()
    article_links = article.xpath('.//strong/a/@href').extract()
    article_summaries = article.xpath('.//div[@class = "description"]/a/text()').extract()
    article_images = article.xpath('.//img/@data-src').re('(\/[^\./]*\.[A-z]*$|\/[^\./]*$|^#$)') # NOTE that sometimes we have empty pic / removed .jpg part
    article_dates = ''
    
    # Now combine into dictionaries
    for i, title in enumerate(article_titles):
        if article_summaries[i]:
            article_summaries[i] = article_summaries[i].strip()

        article_info = {
            'article_title' : title.strip(),
            'article_link' : article_links[i],
            'article_summary' : article_summaries[i],
            'article_image' : article_images[i].replace('_', '').replace('\..*$', '').replace('_', ' '),
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
    story_body = sel.xpath('//p//text() | //span[@class = "caption"]/text()').extract()
    story_text = ''.join(story_body)

    story_author = sel.xpath('//meta[@property = "article:author"]/@content').extract_first()

    story_date = sel.xpath('//meta[@property = "article:published_time"]/@content').extract_first()
    
    # Twitter is blank
    story_twitter = ''
    
    story_keywords = sel.xpath('//meta[@name = "keywords"]/@content').extract()

    # Return in this order specifically
    return story_text, story_author, story_date, story_twitter, story_keywords