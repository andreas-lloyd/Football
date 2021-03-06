'''
Functions included
- Find sublinks
- Find headlines
- Find stories
'''
import parsel as pr

def get_suburls(html_path):
    print('Processing the HTML found in \n{}'.format(html_path))
    
    with open(html_path, 'r', encoding = 'utf-8') as html_file:
        html_content = html_file.read()
    
    sel = pr.Selector(html_content)

    links = sel.xpath('//a[contains(@href, "teampages")]/@href').extract()
    return ['http://www.dailymail.co.uk' + link for link in links]


def extract_headlines(html_content, modifier):
    '''
    Extract headlines from the HTML content of Dailymail articles
    Note that we have 3 URL types - 2x Base and sublinks
    The modifier points to the team pages
    '''
    sel = pr.Selector(html_content)
    articles_info = {}
    
    if modifier: # OR premierleague index
        # This skips the first story - but unclear if really want this one (seems more like a discussion piece)
        article = sel.xpath('//div[@class = "article article-small articletext-right"]')
        
        article_titles = article.xpath('./h2/a/text()').extract() # add in /h2/a
        article_links = article.xpath('./h2/a/@href').extract()
        article_summaries = article.xpath('./p[not(@class)]/text()').extract()
        article_images = ['']*len(article_titles)
        article_dates = sel.xpath('.//div[@class = "channel-date-container sport"]/span/text()').extract()
    
    else:
        # Have two types of articles - small and big - all start with this article format - THERE MAY BE MORE TO EXTRACT
        article = sel.xpath('//div[contains(@class, "article article-")]')
        
        article_titles = article.xpath('.//a[@itemprop = "url"]/text()').extract()
        article_links = article.xpath('.//a[@itemprop = "url"]/@href').extract()
        article_summaries = article.xpath('.//p/text()').extract()
        article_images = article.xpath('.//img/@alt').extract()
        article_dates = ['']*len(article_titles)
        
    # Now combine into dictionaries
    for i, title in enumerate(article_titles):

        if article_summaries[i]:
            article_summaries[i] = article_summaries[i].strip()
        
        # Add on to make full URL - note that sometimes it has different format
        if 'www' not in article_links[i]:
            article_links[i] = 'http://www.dailymail.co.uk' + article_links[i]
        
        article_info = {
            'article_title' : title.strip(),
            'article_link' : article_links[i],
            'article_summary' : article_summaries[i],
            'article_image' : article_images[i],
            'article_date' : article_dates[i]
        }

        articles_info['article_{}'.format(i + 1)] = article_info
        
    return articles_info