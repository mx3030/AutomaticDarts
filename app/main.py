import configparser
import sys
import os
import threading
from pipeHandler import PipeHandler
from calibration.calibrationHandler import CalibrationHandler

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    app_config = {
        'ws_host': config.get('App', 'ws_host'),
        'ws_port': config.getint('App', 'ws_port'),
    }
    return app_config
 
if __name__ == "__main__": 
    
    #-------------------------------
    #-------- pipeHandler ----------
    #-------------------------------
    
    if len(sys.argv) < 2:
        print("Usage: python program.py <PIPE_PATH>")
        sys.exit(1)

    pipe_path = sys.argv[1]     

    pipeHandler = PipeHandler(pipe_path)
    pipe_thread = threading.Thread(target=pipeHandler.start)
    pipe_thread.start()
    
    #-------------------------------
    #------ calibrationHandler -----
    #-------------------------------

    config_name = 'config.ini'
    config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), config_name)
    app_config = read_config(config_path)
    
    WS_HOST = app_config['ws_host']
    WS_PORT = app_config['ws_port']

    calibrationHandler = CalibrationHandler(WS_HOST, WS_PORT, pipeHandler)
