'''
Functions included
- Find headlines
- Find stories
'''
import parsel as pr

def extract_headlines(html_content, modifier, logger):
    '''
    Extract headlines from Skysports pages
    The modifier points to regional articles or not
    '''

    sel = pr.Selector(html_content)
    articles_info = {}
    
    if modifier:
        # For the regional articles, would like to tag on the source
        sources = sel.xpath('//div[@class = "paper-stories"]')
        article_titles = []
        for source in sources:
            source_name = source.xpath('.//p/text()').extract_first()
            article_titles.extend([source_name + ' - ' + title for title in source.xpath('.//li//text()').extract()]) # Skybet means need // for text
        
        # Fill in rest with blanks or filler data (links - for title of file)
        article_links = ['/fake_link/article_' + str(i) for i in range(0, len(article_titles))]
        article_summaries = ['']*len(article_titles)
        article_images = ['']*len(article_titles)
        article_dates = ['']*len(article_titles)
        
    else:
        # Note that there is a "show more" section that cannot load HTML for and three different types of article in general
        transfer_headlines = sel.xpath('//div[@class = "box media -vertical -bp20-horizontal"]')
        transfer_sublines = sel.xpath('//div[@class = "box media -bp30-vertical"]')
        transfer_sublinks = sel.xpath('//ul[@class = "list -bullet text-s"]')
        
        # For main headlines
        article_titles = transfer_headlines.xpath('.//a[@class = "-a-block -clear"]/h2/text()').extract()
        article_links = transfer_headlines.xpath('.//a[@class = "-a-block -clear"]/@href').extract()
        article_summaries = transfer_headlines.xpath('.//a[@class = "-a-block -clear"]/p/text()').extract()
        article_images = transfer_headlines.xpath('.//img/@data-src').re('(\/[^\./]*\.[A-z]*|#)') # Found one with a ? in the middle
        article_dates = ['']*len(article_titles)
        
        # For subheadlines
        article_titles.extend(transfer_sublines.xpath('.//h2/text()').extract())
        article_links.extend(transfer_sublines.xpath('.//a[not(@class)]/@href').extract())
        article_summaries.extend(transfer_sublines.xpath('.//a[not(@class)]/p/text()').extract())
        article_images.extend(transfer_sublines.xpath('.//img/@alt | .//img/@data-src').extract()) # Not sure how to extract one and re the other
        article_dates.extend(transfer_sublines.xpath('.//h5[@class = "caption"]/text()').extract())

        # Sublinks in headlines
        sublink_titles = transfer_sublinks.xpath('./li/a/text()').extract() # get the titles to fill in blanks later
        article_titles.extend(sublink_titles)
        article_links.extend(transfer_sublinks.xpath('./li/a/@href').extract())
        article_summaries.extend(['']*len(sublink_titles))
        article_images.extend(['']*len(sublink_titles))
        article_dates.extend(['']*len(sublink_titles))
        
    # Now combine into dictionaries
    for i, title in enumerate(article_titles):
        if article_summaries[i]:
            article_summaries[i] = article_summaries[i].strip()

        if article_links[i] != '' and '://www' not in article_links[i]:
            article_links[i] = 'http://www.skysports.com' + article_links[i]

        article_info = {
            'article_title' : title.strip(),
            'article_link' : article_links[i],
            'article_summary' : article_summaries[i],
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
    story_body = sel.xpath('//p[not(ancestor::ul[@class = "listblock"]) and not(@class = "site-footer__copyright")]/text()').extract()
    story_text = ''.join(story_body)

    # Rest are blank 
    story_author = ''
    story_date = ''
    story_twitter = ''
    story_keywords = [''] 

    # Return in this order specifically
    return story_text, story_author, story_date, story_twitter, story_keywords