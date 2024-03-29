import asyncio
import json
import pickle
import os
import time
from aiortc import RTCPeerConnection, RTCSessionDescription 

class WebRTCHandler():
    def __init__(self, pipe_path):
        self.pc = self.createPeerConnection()
        self.frame = None
        self.pipe_path = pipe_path
        if not os.path.exists(self.pipe_path):
            os.mkfifo(self.pipe_path)
        self.pipe = None
        self.pipe_running = False
    
    def createPeerConnection(self):
        pc = RTCPeerConnection()

        @pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print("Connection state is %s" % pc.connectionState)
            if pc.connectionState == "failed":
                await pc.close()

        @pc.on("track")
        async def on_track(track):
            if track.kind == "video":  
                while True:
                    frame = await track.recv()
                    if self.pipe_running:
                        frame_pickled = pickle.dumps(frame.to_ndarray(format="bgr24"), protocol=pickle.HIGHEST_PROTOCOL)
                        self.pipe.write(frame_pickled)
                        self.pipe.flush()

        return pc

    async def handleOffer(self, data, websocket):
        desc = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
        await self.pc.setRemoteDescription(desc)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        data =  {
            "sdp": self.pc.localDescription.sdp, 
            "type": self.pc.localDescription.type
        }
        answer = {
            "topic" : "answer",
            "data" : data
        }
        await websocket.send(json.dumps(answer))

    def startPipe(self):
        self.pipe = open(self.pipe_path, 'wb')
        self.pipe_running = True
         
    def stopPipe(self):
        if self.pipe:
            self.pipe.close()
            self.pipe = None
            self.pipe_running = False 
