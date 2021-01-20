#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

import pymongo

from crawler.settings import (MONGO_DATABASE, MONGO_HOST, MONGO_PORT,
                              MONGO_PWD, MONGO_USER)


class DB:

    def __init__(self, host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER, password=MONGO_PWD, db_name=MONGO_DATABASE):
        self.client = pymongo.MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PWD,
            authSource=MONGO_DATABASE
        )
        self.db = self.client[MONGO_DATABASE]

    def __create_ttl(self, collect, column):
        collect.create_index(column, expireAfterSeconds=0)

    def update_ua(self, docs):
        self.db['ua'].insert_many(docs)

    def random_ua(self):
        UA = self.db['ua']
        ua_counts = UA.count_documents({})
        random_int = random.randint(0, ua_counts-1)
        res = UA.find({}).limit(1).skip(random_int)
        return list(res)[0].get('ua')

    def random_ip(self):
        IP = self.db['ip']
        ip_counts = IP.count_documents({})
        if ip_counts > 1:
            random_int = random.randint(0, ip_counts-1)
            ip = IP.find({}).limit(1).skip(random_int)
            return list(ip)[0]
        else:
            raise Exception('没有可用的IP')

    def insert_ips(self, ips):
        col = self.db['ip']
        indexes = col.list_indexes()
        if len(list(indexes)) != 2:
            print('没有创建ttl索引')
            self.__create_ttl(col, 'expire_time')
        self.db['ip'].insert_many(ips)
