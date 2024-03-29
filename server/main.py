import configparser
import threading
import os
from server import start_http
from ws import start_ws

def read_config(config_dir, config_name):
    config_path = os.path.join(config_dir, config_name)
    config = configparser.ConfigParser()
    config.read(config_path)

    server_config = {
        'host': config.get('Server', 'host'),
        'port': config.getint('Server', 'port'),
        'ws_port': config.getint('Server', 'ws_port'),
        'client_dir': os.path.join(config_dir, config.get('Server', 'client_dir')),
        'ssl_key': os.path.join(config_dir, config.get('Server', 'ssl_key')),
        'ssl_cert': os.path.join(config_dir, config.get('Server', 'ssl_cert')),
        'pipes_dir': os.path.join(config_dir, config.get('Calc', 'pipes_dir'))
    }
    return server_config


if __name__ == '__main__':
    server_config = read_config('../', 'config.ini')
    HOST = server_config['host']
    PORT = server_config['port']
    WS_PORT = server_config['ws_port']
    CLIENT_DIR = server_config['client_dir']
    SSL_KEY = server_config['ssl_key']
    SSL_CERT = server_config['ssl_cert']
    PIPES_DIR = server_config['pipes_dir']

    # Start WebSocket server in different thread
    ws_thread = threading.Thread(target=start_ws, args=(HOST, WS_PORT, SSL_KEY, SSL_CERT, PIPES_DIR))
    ws_thread.start()

    # Start HTTP server
    # also pass WS_PORT for dynamically inserting in served js code
    start_http(HOST, PORT, WS_PORT, CLIENT_DIR, SSL_KEY, SSL_CERT)

