import asyncio
import websockets
import ssl
import json
import sys
from ws_handlers.webrtcHandler import WebRTCHandler

def start_ws(host, ws_port, ssl_key, ssl_cert):
    loop = asyncio.new_event_loop()  # Create a new event loop for this thread
    asyncio.set_event_loop(loop)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_cert, ssl_key)
    wsServer = WS_Server()
    start_server = websockets.serve(wsServer.listen, host, ws_port, ssl=ssl_context)
    print('starting websocket server on wss://%s:%d' % (host, ws_port))
    try:
        loop.run_until_complete(start_server)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

class WS_Server:
    def __init__(self):
        self.clients = {}

    async def listen(self, websocket, path):  
        client_ip = websocket.remote_address[0]
        webrtcHandler = WebRTCHandler()
        self.clients[client_ip] = {
            "ws" : websocket
        }
        try:
            async for message in websocket:  
                temp = json.loads(message)
                topic = temp.get('topic', '')
                data = temp.get('data', '')
               
                if topic == 'position':
                    print("position received")
                    position = data["position"]
                    self.clients[client_ip]["position"] = position  
                elif topic == "offer":
                    print("offer received")
                    await webrtcHandler.handleOffer(data, websocket)
                
                print(self.clients)

        except websockets.exceptions.ConnectionClosedOK:
            print(f"connection closed for client {websocket.remote_address}")

    


        


