import scrapy
from crawler.db import DB
from crawler.items import CrawlerItem
from scrapy.exceptions import CloseSpider


class MercadorSpider(scrapy.Spider):
    name = 'mercador'
    allow_donmin = ['listado.mercadorlibre.com', 'exercise.kingname.info']
    db = DB().db
    
    # 爬取策略根据指定策略参数strategy和当前关键词历史决定
    # 如果有爬取历史，则考虑指定策略
    # 如果没有爬取历史，则默认完整爬取策略
    # strategy:
    # 0: 仅仅追踪有结果的数据
    # 1: 完整爬取关键词所有结果
    def start_requests(self):
        strategy = 0
        try:
            strategy = int(self.strategy)
            print(f'使用指定策略：{strategy}')
        except Exception as e:
            print('使用默认追踪策略')

        col = f'kw-{self.keyword}'
        cols = self.db.list_collection_names(filter={"name":{"$regex":r"^kw-"}})
        if not col in cols:
            yield scrapy.Request(f'https://listado.mercadolibre.com.mx/{self.keyword}')
        else:
            if strategy:
                yield scrapy.Request(f'https://listado.mercadolibre.com.mx/{self.keyword}')
            else:
                docs_cursor = self.db[col].aggregate([{'$group': {'_id': { 'pid': '$pid' }, 'pid': {'$last': '$pid'} ,  'src': {'$last': '$src'}, 'sales': {'$last': '$sales'}}},{'$match': {'sales': {'$gt': 0}}}])
                docs = list(docs_cursor)
                if not len(docs) > 0:
                    yield scrapy.Request(f'https://listado.mercadolibre.com.mx/{self.keyword}')
                else:
                    for doc in docs:
                        item = CrawlerItem()
                        item['src'] = doc['src']
                        item['pid'] = doc['pid']
                        yield scrapy.Request(item['src'],self.parse_item,cb_kwargs={'item':item})

    def parse(self, response):
        # 当前页产品处理
        products = response.css('.ui-search-layout__item')
        for product in products:
            item = CrawlerItem()
            item['src'] = product.xpath('.//a[@class="ui-search-link"]/@href').get()
            item['pid'] = product.xpath('.//input[@name="itemId"]/@value').get()
            yield scrapy.Request(item['src'],self.parse_item,cb_kwargs={'item':item})

        # 下一页
        next_page = response.css('a[title="Siguiente"]')
        if(next_page):
            url = response.css('a[title="Siguiente"]').attrib['href']
            yield scrapy.Request(url, self.parse)

    def parse_item(self, response, item):
        img_pc = response.xpath("//img[@class='ui-pdp-image ui-pdp-gallery__figure__image']/@src").get()
        if(img_pc):
            item['img'] = img_pc
            item['price'] = response.css('meta[itemprop="price"]').xpath('@content').get()
            item['stock'] = response.css('span[class*="quantity__available"]::text').re_first('\d+')

        else:
            item['img'] = response.xpath("//img[@class='ui-pdp-image ui-pdp-gallery--horizontal']/@src").get()
            item['price'] = response.xpath("//div[@class='ui-pdp-price__second-line']//span[@class='price-tag-fraction']/text()").get()
            item['stock'] = response.css('.ui-pdp-action-row__subtitle::text').re_first('\d+')
        
        sales = response.css('.ui-pdp-subtitle::text').re_first('\d+')
        item['sales'] = int(sales) if sales else 0 
        item['title'] = response.css('.ui-pdp-title::text').get()
        yield item
