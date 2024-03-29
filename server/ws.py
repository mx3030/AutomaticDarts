import asyncio
import websockets
import ssl
import json
import os
import subprocess
from webrtcHandler import WebRTCHandler

def start_ws(host, ws_port, ssl_key, ssl_cert, app_main, pipes_dir):
    """
    create new event loop for websocket thread+
    """
    loop = asyncio.new_event_loop() 
    asyncio.set_event_loop(loop)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(ssl_cert, ssl_key)
    wsServer = WS_Server(app_main, pipes_dir)
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
    def __init__(self, app_main, pipes_dir):
        self.camera_clients = {}
        self.app_main = app_main
        self.pipes_dir = pipes_dir
    
    async def router(self,websocket, path):
        if path == "/camera":
            await self.handleCamera(websocket) 
        
    async def handleCamera(self, websocket):  
        """
        handle connection from camera client
        """ 
        client_ip = websocket.remote_address[0]
        pipe_path = os.path.join(self.pipes_dir, client_ip)
        webrtcHandler = WebRTCHandler()    

        try:
            async for message in websocket:  
                temp = json.loads(message)
                topic = temp.get('topic', '')
                data = temp.get('data', '')
               
                if topic == "offer":
                    await webrtcHandler.handleOffer(data, websocket) 
                elif topic == "start":
                    command = f'python3 {self.app_main} {os.path.abspath(pipe_path)}'
                    app_process = subprocess.Popen(['python3', self.app_main, os.path.abspath(pipe_path)])
                    webrtcHandler.startPipe(pipe_path)
                elif topic == "stop":
                    app_process.terminate()
                    webrtcHandler.stopPipe()
        
        except websockets.exceptions.ConnectionClosedOK:
            print(f"connection closed for client {websocket.remote_address}")       
