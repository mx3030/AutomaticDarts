import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate 
from ws_handlers.streamHandler import StreamHandler

class WebRTCHandler():
    def __init__(self):
        super().__init__()
        self.contentType = 'application/json'
        self.pc = self.createPeerConnection()
        self.streamHandler = StreamHandler()

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
                # if track is not consumed --> memory leak
                self.streamHandler.setTrack(track)
                self.streamHandler.start()
                
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

