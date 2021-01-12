import asyncio

from aiohttp import web
from scrapy import cmdline

routes = web.RouteTableDef()

@routes.get('/run/{keyword}')
async def run_crawler(request):
    keyword = request.match_info['keyword']
    cmdline.execute(f'scrapy crawl mercador -a keyword={keyword}'.split())
    return web.json_response(text='爬虫已成功启动')

@routes.get('/')
async def index(request):
    return web.Response(text='Index')

@routes.get('/hello/{name}')
async def hello(request):
    await asyncio.sleep(0.5)
    text = '<h1>hello, %s!</h1>' % request.match_info['name']
    return web.Response(text=text)

@routes.get('/ws')
async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws

# async def init():
#     app = web.Application(loop=loop)
#     app.router.add_route('GET', '/', index)
#     app.router.add_route('GET', '/hello/{name}', hello)
#     srv = await loop.create_server(app.make_handler(), '127.0.0.1', 8086)
#     print('Server started at http://127.0.0.1:8086...')
#     return srv

# loop = asyncio.get_event_loop()
# loop.run_until_complete(init(loop))
# loop.run_forever()

app = web.Application()
app.add_routes(routes)
web.run_app(app, host='localhost')
