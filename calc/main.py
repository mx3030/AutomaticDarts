import configparser
import os
import json
import cv2
import pickle
from websockets.sync.client import connect

def read_config(config_dir, config_name):
    config_path = os.path.join(config_dir, config_name)
    config = configparser.ConfigParser()
    config.read(config_path)

    app_config = {
        'host': config.get('Server', 'host'),
        'ws_port': config.getint('Server', 'ws_port'),
        'pipes_dir': os.path.join(config_dir, config.get('Calc', 'pipes_dir')),
    }
    
    return app_config

def get_available_pipes(pipes_dir):
    return [os.path.join(pipes_dir, pipe_name) for pipe_name in os.listdir(pipes_dir)]

def read_pipe(pipe_path):
    with open(pipe_path, 'rb') as pipe:
        while True:
            try:
                data = pickle.load(pipe)
                cv2.imshow('test', data)
            except EOFError:
                break
                
class WS_Client:
    def __init__(self, host, port):
        conn_string = f"wss://{host}:{port}/calc"
        self.ws = connect(conn_string)

    def send(self, message):
        self.ws.send(json.dumps(message))


def start_pipe_writing(ws, pipe_name):
    data = {
        "ip": pipe_name
    }
    message = {
        "topic": "start",
        "data" : data
    }
    ws.send(message)

def stop_pipe_writing(ws, pipe_name):
    data = {
        "ip": pipe_name
    }
    message = {
        "topic": "stop",
        "data" : data
    }
    ws.send(message)


if __name__ == "__main__":
    app_config = read_config('../', 'config.ini')
    
    HOST = app_config['host']
    WS_PORT = app_config['ws_port']
    PIPES_DIR = app_config['pipes_dir']
    
    wsClient = WS_Client(HOST, WS_PORT)
    available_pipes = get_available_pipes(PIPES_DIR)
    try:
        for pipe_name in available_pipes:
            start_pipe_writing(wsClient, pipe_name)
            read_pipe(pipe_name)
    except KeyboardInterrupt:
        for pipe_name in available_pipes:
            stop_pipe_writing(wsClient, pipe_name)
        wsClient.ws.close()
        cv2.destroyAllWindows()
