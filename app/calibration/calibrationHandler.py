from calibration.wsHandler import WSHandler

class CalibrationHandler:
    def __init__(self, ws_host, ws_port, pipeHandler):
        self.pipeHandler = pipeHandler
        pair_id = self.pipeHandler.pipe_path
        self.ws = WSHandler(self, ws_host, ws_port, pair_id)
    
    def getFrameData(self):
        frame = self.pipeHandler.getFrame()
        return frame

    def sendFrame(self):
        frame_data = self.getFrameData()
        print(frame_data) 
