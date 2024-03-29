import cv2
import pickle
import time

class PipeHandler:
    def __init__(self, pipe_path):
        self.pipe_running = False
        self.pipe_path = pipe_path
    
    def start(self):
        self.pipe_running = True
        time.sleep(2) 
        with open(self.pipe_path, 'rb') as pipe:
            try:
                while self.pipe_running:
                    frame = pickle.load(pipe)
                    cv2.imshow('test', frame)
                    cv2.waitKey(1)
            except EOFError:
                cv2.destroyAllWindows()
            finally:
                cv2.destroyAllWindows() 

    def stop(self):
        self.pipe_running = False

