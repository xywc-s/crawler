#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

import pymongo

# from crawler.settings import MONGO_DATABASE, MONGO_URI
from settings import MONGO_DATABASE, MONGO_URI


class DB:

    def __init__(self, uri=MONGO_URI, db_name=MONGO_DATABASE):
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DATABASE]

    def __create_ttl(self, collect, column):
        collect.create_index(column, expireAfterSeconds=0)

    def insert_ips(self, ips):
        col = self.db['ip']
        indexes = col.list_indexes()
        if len(list(indexes)) != 2:
            print('没有创建ttl索引')
            self.__create_ttl(col, 'expire_time')
        return self.db['ip'].insert_many(ips)

    def random_ip(self):
        IP = self.db['ip']
        ip_counts = IP.count_documents({})
        if ip_counts > 1:
            random_int = random.randint(0, ip_counts-1)
            ip = IP.find({}).limit(1).skip(random_int)
            return list(ip)[0]
        else:
            raise '没有可用的IP'
