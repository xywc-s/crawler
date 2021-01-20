# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from crawler.db import DB


class CrawlerPipeline:

    items = []

    def __init__(self, mongo=DB):
        self.db = mongo().db

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter['created_at'] = datetime.now().timestamp()
        self.items.append(adapter.asdict())
        self.db[f'kw-{spider.keyword}'].insert_one(adapter.asdict())
        return f"成功抓取关键词 [ {spider.keyword} ] 下的产品 {item['pid']} "

    def open_spider(self, spider):
        print(f'爬虫{spider.name}已打开,数据库已连接')

    def close_spider(self, spider):
        if(self.items):
            print(f'爬虫 {spider.name} 已关闭 : 成功爬取到{len(self.items)}条数据')
        else:
            print(f'爬虫 {spider.name} 已关闭 : 没有爬取到任何数据')
        


class DuplicatesPipeline:

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['pid'] in self.ids_seen:
            raise DropItem(f"发现重复产品: {item['pid']}")
        else:
            self.ids_seen.add(adapter['pid'])
            return item

class SalesFilterPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter['sales']:
            raise DropItem(f"{item['pid']}没有销量,直接丢弃")
        else:
            return item
