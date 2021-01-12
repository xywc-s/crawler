# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pid = scrapy.Field()
    keyword = scrapy.Field()
    src = scrapy.Field()
    img = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    sales = scrapy.Field()
    stock = scrapy.Field()
    variations = scrapy.Field()
    created_at = scrapy.Field()
