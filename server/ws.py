import asyncio
import websockets
import ssl
import json
import os
from webrtcHandler import WebRTCHandler

def start_ws(host, ws_port, ssl_key, ssl_cert, pipes_dir):
    """
    create new event loop for websocket thread
    """
    loop = asyncio.new_event_loop() 
    asyncio.set_event_loop(loop)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_cert, ssl_key)
    wsServer = WS_Server(pipes_dir)
    start_server = websockets.serve(wsServer.router, host, ws_port, ssl=ssl_context)
    print('starting websocket server on wss://%s:%d' % (host, ws_port))
    try:
        loop.run_until_complete(start_server)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

class WS_Server:
    def __init__(self, pipes_dir):
        self.clients = {}
        self.pipes_dir = pipes_dir
    
    async def router(self,websocket, path):
        if path == "/camera":
            await self.handleCams(websocket)
        elif path == "/calc":
            await self.handleCalc(websocket)

    async def handleCams(self, websocket):  
        """
        handle ios cam devices
        """ 
        client_ip = websocket.remote_address[0]
        pipe_path = os.path.join(self.pipes_dir, client_ip)
        webrtcHandler = WebRTCHandler(pipe_path)    
        self.clients[client_ip] = webrtcHandler
        
        try:
            async for message in websocket:  
                temp = json.loads(message)
                topic = temp.get('topic', '')
                data = temp.get('data', '')
               
                if topic == "offer":
                    await webrtcHandler.handleOffer(data, websocket)                            
        
        except websockets.exceptions.ConnectionClosedOK:
            print(f"connection closed for client {websocket.remote_address}")  

    async def handleCalc(self, websocket):
        """
        handle calc test
        """
        try: 
            async for message in websocket:
                temp = json.loads(message)
                topic = temp.get('topic', '')
                data = temp.get('data', '')

                cam_ip = data['ip']
                if cam_ip in self.clients:
                    webrtcHandler = self.clients[cam_ip]
                    if topic == "start":
                        print("start signal")
                        webrtcHandler.startPipe()
                    elif topic == "stop":
                        webrtcHandler.stopPipe()

        except websockets.exceptions.ConnectionClosedOK:
            print(f"connection closed for client {websocket.remote_address}")
