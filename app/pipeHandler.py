import cv2
import pickle
import time

class PipeHandler:
    def __init__(self, pipe_path):
        self.pipe_running = False
        self.pipe_path = pipe_path
        self.frame = None
    
    def start(self):
        self.pipe_running = True
        time.sleep(2) 
        with open(self.pipe_path, 'rb') as pipe:
            while self.pipe_running:
                self.frame = pickle.load(pipe)  

    def getFrame(self):
        return self.frame

