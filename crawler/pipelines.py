# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime

import pymongo
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CrawlerPipeline:

    items = []

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter['created_at'] = datetime.now().timestamp()
        self.items.append(adapter.asdict())
        self.db[f'kw-{spider.keyword}'].insert_one(adapter.asdict())
        return f"成功抓取关键词 [ {spider.keyword} ] 下的产品 {item['pid']} "

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        print(f'爬虫{spider.name}已打开,数据库{self.mongo_db}已连接')

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
            raise DropItem(f"发现重复产品: {item!r}")
        else:
            self.ids_seen.add(adapter['pid'])
            return item
