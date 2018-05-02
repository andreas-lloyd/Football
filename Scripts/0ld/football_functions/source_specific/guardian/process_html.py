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
    
    return sel.xpath('//div[@class = "fc-item fc-item--list-compact"]/a/@href').extract()

def extract_headlines(html_content):
    '''
    Extract headlines from HTML content from the Guardian team pages
    '''
    sel = pr.Selector(html_content)
    articles_info = {}
    
    # All articles seem to start with this
    articles = sel.xpath('//div[@class = "fc-item__container"]')
    
    # Because some do not have summaries etc. will loop over
    for i, article in enumerate(articles):
        article_title = article.xpath('./a/text()').extract_first() # since there is H2 ahead of first a, should be OK
        article_link = article.xpath('./a/@href').extract_first()
        article_summary = article.xpath('.//div[@class = "fc-item__standfirst"]/text()').extract_first()
        article_image = ''
        article_date = article.xpath('.//time/@datetime').extract_first()

        if article_summary:
            article_summary = article_summary.strip()

        article_info = {
            'article_title' : article_title.strip(),
            'article_link' : article_link,
            'article_summary' : article_summary,
            'article_image' : article_image,
            'article_date' : article_date
        }

        articles_info['article_{}'.format(i + 1)] = article_info
    
    return articles_info