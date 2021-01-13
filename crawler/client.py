#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from datetime import datetime, timedelta

from aiohttp import ClientSession

from db_client import DB

# '领取免费套餐'='ty-http-d.hamir.net/index/index/get_my_package_balance?neek=550872&appkey=af1d1515e8f50b77bb9a310d3d7d30c8&ac=61371'

# '提取IP'='http://http.tiqu.alibabaapi.com/getip?num=1&type=2&pack=61371&port=1&ts=1&ys=1&cs=1&lb=1&pb=4&regions='

# 请求地址
# targetUrl = "https://www.baidu.com"

# 代理服务器
# proxyHost = "ip"
# proxyPort = "port"

# proxyMeta = f"http://{proxyHost}:{proxyPort}"

# proxies = {
#     "http"  : proxyMeta,
#     "https"  : proxyMeta
# }

# resp = requests.get(targetUrl, proxies=proxies)
# print resp.status_code
# print resp.text

login_info = {"phone": "15307209981", "password": "W8J&s&%2sE"}

headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'Host': 'ty-http-d.hamir.net',
    'Origin': 'http://taiyanghttp.tuquan.shop',
    'Referer': 'http://taiyanghttp.tuquan.shop/',
    'session-id': 'i9qf59jmfbkh05oojrcdqfch55',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
}


async def get_ip():
    async with ClientSession() as session:
        async with session.get('http://http.tiqu.alibabaapi.com/getip?num=1&type=2&pack=61371&port=1&ts=1&ys=1&cs=1&lb=1&pb=4&regions=') as res:
            res = json.loads(await res.text())
            print('res', res)
            if res['success']:
                ips = res['data']
                for ip in ips:
                    ip['expire_time'] = datetime.utcfromtimestamp((datetime.strptime(ip['expire_time'], '%Y-%m-%d %H:%M:%S') - timedelta(minutes=3)).timestamp())
                res = DB().insert_ips(ips)
                print(f'成功提取{len(res.inserted_ids)}个IP')
            else:
                raise '太阳IP提取失败'


async def get_proxy():
    async with ClientSession() as session:
        async with session.get('http://ty-http-d.hamir.net/index/index/get_my_package_balance?neek=550872&appkey=af1d1515e8f50b77bb9a310d3d7d30c8&ac=61371') as res:
            res = json.loads(await res.text())
            if res['success']:
                print('领取套餐成功')
                await get_ip()
            else:
                print('领取套餐失败')


async def taiyang_proxy():
    async with ClientSession() as session:
        async with session.post('http://ty-http-d.hamir.net/index/login/dologin', data=login_info) as res:
            res = json.loads(await res.text())
            if int(res['code']) == 1:
                headers['session-id'] = res['ret_data']
                async with session.get('http://ty-http-d.hamir.net/index/users/get_day_free_pack', headers=headers) as res:
                    res = json.loads(await res.text())
                    print('res', res)
                    if int(res['code']) == 1 or int(res['code']) == -1:
                        print('免费套餐领取成功')
                        await get_ip()
                    else:
                        print('免费套餐领取失败')
            else:
                print('太阳代理登陆失败')


async def crawler():
    async with ClientSession() as session:
        async with session.get('http://localhost:8080/run/gloves') as resp:
            print(await resp.text(), '开始爬取关键词 - gloves')
        async with session.get('http://localhost:8080/run/camara-hdcvi-bullet') as resp:
            print(await resp.text(), '开始爬取关键词 - camara-hdcvi-bullet')

loop = asyncio.get_event_loop()

# 获取IP
# loop.run_until_complete(get_ip())

# 直接领取
# loop.run_until_complete(get_proxy())

# 登录后领
loop.run_until_complete(taiyang_proxy())

# 开启爬虫 - 需要开启爬虫服务器
# loop.run_until_complete(crawler())


# if __name__ == '__main__':
#     db = DB()
#     ips = [{
#         "city": "江苏省淮安市", "port": "4317", "ip": "49.87.117.187", "isp": "电信", "expire_time": "2021-01-12 14:40:11"
#     }, {
#         "city": "辽宁省鞍山市", "port": "4330", "ip": "124.94.255.205", "isp": "联通", "expire_time": "2021-01-12 14:41:48"
#     }, {
#         "city": "福建省南平市", "port": "4378", "ip": "59.59.149.211", "isp": "电信", "expire_time": "2021-01-12 14:42:44"
#     }]
#     for ip in ips:
#         # ip['expire_time'] = (datetime.strptime(ip['expire_time'], '%Y-%m-%d %H:%M:%S') - timedelta(minutes=3)).timestamp()
#         ip['expire_time'] = datetime.utcfromtimestamp((datetime.strptime(ip['expire_time'], '%Y-%m-%d %H:%M:%S') - timedelta(minutes=3)).timestamp())

#     db.insert_ips(ips)
#     cols = db.db.list_collection_names()
#     print(cols)
