from aiortc import VideoStreamTrack
import cv2
import asyncio

class StreamHandlerHandler:
    def __init__(self):
        self.track = None

    def setTrack(self, track):
        self.track = track

    def getTrack(self):
        return self.track
    
    def start(self):
        while True:
            frame = await self.track.recv()
