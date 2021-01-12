import scrapy
from crawler.items import CrawlerItem
from scrapy.exceptions import CloseSpider


class MercadorSpider(scrapy.Spider):
    name = 'mercador'
    allow_donmin = ['listado.mercadorlibre.com', 'exercise.kingname.info']
    
    def start_requests(self):
        yield scrapy.Request(f'https://listado.mercadolibre.com.mx/{self.keyword}')

    def parse(self, response):
        # 当前页产品处理
        i = 0
        products = response.css('.ui-search-layout__item')
        for product in products:
            item = CrawlerItem()
            item['src'] = product.xpath('.//a[@class="ui-search-link"]/@href').get()
            item['pid'] = product.xpath('.//input[@name="itemId"]/@value').get()
            yield scrapy.Request(item['src'],self.parse_item,cb_kwargs={'item':item})
            i = i+1
            if(i==6):
                break

        # 下一页
        # next_page = response.css('a[title="Siguiente"]')
        # if(next_page):
        #     url = response.css('a[title="Siguiente"]').attrib['href']
        #     yield scrapy.Request(url, self.parse)

    def parse_item(self, response, item):
        item['img'] = response.css('.ui-pdp-image').xpath('./@src').getall()[0]
        item['sales'] = response.css('.ui-pdp-subtitle::text').re_first('\d+')
        item['title'] = response.css('.ui-pdp-title::text').get()
        item['price'] = response.css(
            'meta[itemprop="price"]').attrib['content']
        item['stock'] = response.css(
            'span[class*="quantity__available"]::text').re_first('\d+')
        yield item
