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
        self.app_main = app_main
        self.pipes_dir = pipes_dir
        self.camera_clients = {}
        self.calibration_offers = set()
        self.calibration_pairs = {} 

    async def router(self,websocket, path):
        if path == "/camera":
            await self.handleCamera(websocket)
        if path == "/calibration":
            await self.handleCalibration(websocket)

    async def handleCamera(self, websocket):  
        """
        handle connection from camera client
        """ 
        client_ip = websocket.remote_address[0]
        pipe_path = os.path.join(self.pipes_dir, client_ip)
        webrtcHandler = WebRTCHandler()    
        app_process = None

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
                    if app_process:
                        app_process.terminate()
                    if webrtcHandler:
                        webrtcHandler.stopPipe()

        except websockets.exceptions.ConnectionClosedOK:
            if app_process:
                app_process.terminate()
            if webrtcHandler:
                webrtcHandler.stopPipe()
            print(f"connection closed for client {websocket.remote_address}")   


    async def handleCalibration(self, websocket):
        """
        handle link between remote interface and local host for calibration of ios camera
        """  
        try:
            async for message in websocket:  
                temp = json.loads(message)
                topic = temp.get('topic', '')
                data = temp.get('data', '')
                
                print(f"ws_server: {topic}")
                
                # ---------------------------------------
                # ------------ local topics -------------
                # ---------------------------------------
                if topic == "start_calibration_offer":
                    # start calibration offer from local app
                    pair_id = data.get("pair_id")
                    self.calibration_offers.add(pair_id)
                    self.calibration_pairs[pair_id] = { "local" : websocket } 
                
                elif topic == "stop_calibration_offer":
                    # stop calibration offer from local app
                    pair_id = data.get("pair_id")
                    if pair_id in self.calibration_offers:
                        self.calibration_offers.remove(pair_id)
                        calibration_pair = self.calibration_pairs.get(pair_id)
                        remote_ws = calibration_pair.get("remote")
                        if remote_ws:
                            await remote_ws.send(message)
                        del self.calibration_pairs[pair_id]
                
                # ---------------------------------------
                # ------------ remote topics ------------
                # --------------------------------------- 
                elif topic == "get_calibration_offers":
                    # send available calibration offers to client
                    data = { "calibration_offers": list(self.calibration_offers) }
                    message = {
                        "topic": "calibration_offers",
                        "data": data
                    }
                    await websocket.send(json.dumps(message))

                elif topic == "join_calibration_pair":
                    # remote client joins calibration pair
                    # if multiple devices want to connect to same pair_id, remote_ws gets overwritten
                    pair_id = data.get("pair_id")
                    calibration_pair = self.calibration_pairs.get(pair_id)
                    if calibration_pair:
                        calibration_pair["remote"] = websocket
                        message = { "topic": "pair_established" }
                        for ws in calibration_pair.values():
                            await ws.send(json.dumps(message))

                elif topic == "disjoin_calibration_pair":
                    # remote client disjoins calibration pair
                    pair_id = data.get("pair_id")
                    calibration_pair = self.calibration_pairs.get(pair_id)
                    if calibration_pair:
                        # inform local host on remote disconnection
                        local_ws = calibration_pair.get("local")
                        if local_ws:
                            message = { "topic": "remote pair disjoined" }
                            await local_ws.send(json.dumps(message))
                        del calibration_pair["remote"]
                
                # ---------------------------------------
                # ------- direct communication ----------
                # ---------------------------------------
                else:
                    pair_id = data.get("pair_id")
                    target = data.get("target")
                    calibration_pair = self.calibration_pairs.get(pair_id)
                    if calibration_pair:
                        target_ws = calibration_pair.get(target)
                        if target_ws:
                            await target_ws.send(message)
                    else:
                        print(f"{pair_id} missing {target} target.")

        except websockets.exceptions.ConnectionClosedOK:
            print(f"connection closed for client {websocket.remote_address}")
