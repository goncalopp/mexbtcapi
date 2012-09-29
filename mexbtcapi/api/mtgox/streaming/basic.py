import httplib, json, pprint

try:
    import websockete
except ImportError as e:
    raise ImportError("You need to install the websocket module. Get it from https://github.com/liris/websocket-client.git")

ws = websocket.WebSocket()
ws.connect('wss://websocket.mtgox.com/mtgox')
while True:
    r= json.loads(ws.recv())
    pprint.pprint(r)
ws.close()
